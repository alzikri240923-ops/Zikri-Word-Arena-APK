const express = require("express");
const http = require("http");
const path = require("path");
const fs = require("fs");
const { Server } = require("socket.io");
const crypto = require("crypto");
const CrosswordEngine = require("./public/crossword-engine");
const MEIQUIZZ_QUESTIONS = require("./data/meiquizz-questions.json");

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: true } });

const PORT = process.env.PORT || 3000;
const GAME_DURATION = 180;
const MAX_PLAYERS = 10;
const MIN_PLAYERS = 2;
const RECONNECT_GRACE_MS = 45000;
const DATA_DIR = path.join(__dirname, "data");
const PROFILES_FILE = path.join(DATA_DIR, "players.json");

app.use(express.static(path.join(__dirname, "public")));

const rooms = new Map();
const profiles = new Map();
const PUZZLE = {
  w1: "IKAN", w2: "NASI", w3: "DUNIA", w4: "OBAT", w5: "NAGA",
  w6: "EMAS", w7: "SAPI", w8: "IKLIM", w9: "AIR"
};

function loadProfiles() {
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    if (!fs.existsSync(PROFILES_FILE)) return;
    const saved = JSON.parse(fs.readFileSync(PROFILES_FILE, "utf8"));
    for (const profile of saved) {
      if (profile && typeof profile.token === "string") profiles.set(profile.token, {
        token: profile.token,
        name: String(profile.name || "").slice(0, 16),
        totalPoints: Number(profile.totalPoints) || 0,
        wins: Number(profile.wins) || 0,
        matches: Number(profile.matches) || 0,
        bestScore: Number(profile.bestScore) || 0,
        usedQuestions: Array.isArray(profile.usedQuestions) ? profile.usedQuestions : [],
        updatedAt: Number(profile.updatedAt) || Date.now()
      });
    }
  } catch (error) {
    console.error("Gagal membaca data pemain:", error.message);
  }
}

function saveProfiles() {
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    const tempFile = PROFILES_FILE + ".tmp";
    fs.writeFileSync(tempFile, JSON.stringify([...profiles.values()], null, 2));
    fs.renameSync(tempFile, PROFILES_FILE);
  } catch (error) {
    console.error("Gagal menyimpan data pemain:", error.message);
  }
}

function leaderboardData() {
  return [...profiles.values()]
    .filter(profile => profile.name)
    .sort((a, b) => b.totalPoints - a.totalPoints || b.wins - a.wins || b.bestScore - a.bestScore)
    .slice(0, 100)
    .map((profile, index) => ({
      rank: index + 1,
      name: profile.name,
      wins: profile.wins,
      matches: profile.matches,
      totalPoints: profile.totalPoints,
      bestScore: profile.bestScore
    }));
}

function publishLeaderboard() {
  io.emit("leaderboard:update", leaderboardData());
}

function makeCode() {
  return crypto.randomBytes(3).toString("hex").toUpperCase();
}

function publicRoom(room) {
  return {
    code: room.code,
    mode: room.mode || "crossword",
    quizSettings: room.mode === "meiquizz" ? room.quizSettings : null,
    quiz: room.mode === "meiquizz" ? { matchType: room.quizSettings?.matchType || "mixed", round: room.quizRound, totalRounds: room.quizSettings?.matchType === "duel" ? 10 : 3, question: room.quizQuestion ? { id: room.quizQuestion.id, question: room.quizQuestion.question, options: room.quizQuestion.options, category: room.quizQuestion.category, difficulty: room.quizQuestion.difficulty } : null, phase: room.quizPhase, questionNumber: room.quizQuestionNumber || 0 } : null,
    puzzle: room.puzzle || null,
    status: room.status,
    seconds: room.seconds,
    maxPlayers: MAX_PLAYERS,
    solved: [...room.solved],
    players: [...room.players.values()].map(player => ({
      id: player.id,
      name: player.name,
      score: player.score,
      isHost: player.id === room.host,
      streak: player.streak,
      connected: player.connected !== false,
      eliminated: !!player.eliminated,
      voiceActive: !!player.voiceActive
    }))
  };
}

function updateRoom(room) {
  io.to(room.code).emit("room:update", publicRoom(room));
}

function recordMatch(room) {
  if (room.recorded) return;
  room.recorded = true;
  const players = [...room.players.values()];
  if (!players.length) return;
  const highScore = Math.max(...players.map(player => player.score));
  for (const player of players) {
    const profile = profiles.get(player.profileToken);
    if (!profile) continue;
    profile.matches += 1;
    profile.totalPoints += player.score;
    profile.bestScore = Math.max(profile.bestScore, player.score);
    if (player.score === highScore && highScore > 0) profile.wins += 1;
    profile.updatedAt = Date.now();
  }
  saveProfiles();
  publishLeaderboard();
}

function finishGame(room) {
  if (room.status !== "playing") return;
  room.status = "finished";
  clearInterval(room.timer);
  room.timer = null;
  recordMatch(room);
  updateRoom(room);
  io.to(room.code).emit("game:finished");
}

function pickQuizQuestion(room) {
  const settings = room.quizSettings || { category: "Campuran", difficulty: "bertahap" };
  let eligible = MEIQUIZZ_QUESTIONS.filter(q =>
    (settings.category === "Campuran" || q.category === settings.category) &&
    (settings.difficulty === "bertahap"
      ? Number(q.difficulty) === (room.quizPhase === "survival" ? 3 : Math.min(room.quizSettings?.matchType === "duel" ? Math.ceil((room.quizQuestionNumber || 1) / 4) : (room.quizRound || 1), 3))
      : Number(q.difficulty) === ({mudah:1, sedang:2, sulit:3}[settings.difficulty] || 0))
  );
  if (!eligible.length) eligible = MEIQUIZZ_QUESTIONS;
  const pool = eligible.filter(q => !room.usedQuizQuestions.has(q.id));
  const source = pool.length ? pool : eligible;
  const q = source[Math.floor(Math.random() * source.length)];
  room.usedQuizQuestions.add(q.id);
  return q;
}
function startMeiquizz(room) {
  room.status = "playing"; room.quizRound = 1; room.quizPhase = room.quizSettings?.matchType === "duel" ? "duel" : "points"; room.quizQuestionNumber = 1;
  room.quizQuestion = pickQuizQuestion(room); room.quizAnswered = new Set(); room.quizSurvivors = new Set([...room.players.keys()]);
  room.seconds = 15; room.recorded = false;
  for (const p of room.players.values()) { p.score = 0; p.streak = 0; p.eliminated = false; }
  updateRoom(room); io.to(room.code).emit("meiquizz:question", publicRoom(room).quiz);
  runQuizTimer(room);
}
function runQuizTimer(room) {
  clearInterval(room.timer); room.timer = setInterval(() => {
    if (room.status !== "playing") return; room.seconds--; io.to(room.code).emit("game:tick", room.seconds);
    if (room.seconds <= 0) advanceQuiz(room);
  }, 1000);
}
function advanceQuiz(room) {
  if (room.status !== "playing" || room.mode !== "meiquizz") return;
  clearInterval(room.timer); room.timer = null;
  if (room.quizPhase === "duel") {
    if (room.quizQuestionNumber >= 10) return finishGame(room);
  } else if (room.quizPhase === "points") {
    if (room.quizRound < 3) room.quizRound++;
    else { room.quizPhase = "survival"; room.quizRound = 4; room.quizSurvivors = new Set([...room.players.values()].filter(p => !p.eliminated).map(p => p.id)); }
  } else {
    const alive = [...room.players.values()].filter(p => !p.eliminated);
    if (alive.length <= 1) return finishGame(room);
    for (const p of alive) if (!room.quizAnswered.has(p.id)) { p.eliminated = true; room.quizSurvivors.delete(p.id); }
    if ([...room.players.values()].filter(p => !p.eliminated).length <= 1) return finishGame(room);
  }
  room.quizQuestionNumber++; room.quizQuestion = pickQuizQuestion(room); room.quizAnswered = new Set(); room.seconds = room.quizPhase === "survival" ? 12 : 15;
  updateRoom(room); io.to(room.code).emit("meiquizz:question", publicRoom(room).quiz); runQuizTimer(room);
}

function startGame(room) {
  if (room.status !== "waiting") return false;
  if (room.mode === "meiquizz") { startMeiquizz(room); return true; }
  const active=[...room.players.values()].filter(p=>p.connected!==false);
  const excluded=[...new Set(active.flatMap(p=>profiles.get(p.profileToken)?.usedQuestions||[]))];
  room.puzzle=CrosswordEngine.generate(excluded,10);
  if(!room.puzzle){for(const p of active){const profile=profiles.get(p.profileToken);if(profile)profile.usedQuestions=[];}room.puzzle=CrosswordEngine.generate([],10);}
  if(!room.puzzle){room.status="waiting";return false;}
  for(const p of active){const profile=profiles.get(p.profileToken);if(profile){profile.usedQuestions=[...new Set([...(profile.usedQuestions||[]),...room.puzzle.words.map(w=>w.id)])];profile.updatedAt=Date.now();}}
  saveProfiles();
  room.status = "playing";
  room.recorded = false;
  room.seconds = GAME_DURATION;
  room.solved.clear();
  for (const player of room.players.values()) {
    player.score = 0;
    player.streak = 0;
  }
  updateRoom(room);
  io.to(room.code).emit("game:tick", room.seconds);
  room.timer = setInterval(() => {
    room.seconds -= 1;
    io.to(room.code).emit("game:tick", room.seconds);
    if (room.seconds <= 0) finishGame(room);
  }, 1000);
  return true;
}

function removePlayer(socket, preserve = false) {
  const code = socket.data.roomCode;
  if (!code) return;
  const room = rooms.get(code);
  socket.data.roomCode = null;
  if (!room) return;
  const player = room.players.get(socket.id);
  socket.leave(code);
  if (preserve && player) {
    player.connected = false;
    player.disconnectedAt = Date.now();
    player.reconnectTimer = setTimeout(() => {
      if (room.players.get(player.id) === player && player.connected === false) {
        room.players.delete(player.id);
        if (room.host === player.id) {
          const next = [...room.players.values()].find(p => p.connected !== false);
          room.host = next ? next.id : null;
        }
        if (room.players.size === 0) {
          clearInterval(room.timer);
          rooms.delete(code);
        } else {
          const connectedCount = [...room.players.values()].filter(p => p.connected !== false).length;
          if (room.status === "playing" && connectedCount < MIN_PLAYERS) finishGame(room);
          else updateRoom(room);
        }
      }
    }, RECONNECT_GRACE_MS);
    updateRoom(room);
    return;
  }
  if (player?.reconnectTimer) clearTimeout(player.reconnectTimer);
  room.players.delete(socket.id);
  if (room.players.size === 0) {
    clearInterval(room.timer);
    rooms.delete(code);
    return;
  }
  if (room.host === socket.id) {
    const next = [...room.players.values()].find(p => p.connected !== false);
    room.host = next ? next.id : null;
  }
  const connectedCount = [...room.players.values()].filter(p => p.connected !== false).length;
  if (room.status === "playing" && connectedCount < MIN_PLAYERS) finishGame(room);
  else updateRoom(room);
}

loadProfiles();

io.on("connection", socket => {
  socket.data.lastChatAt = 0;

  // Identitas pemain disimpan di server dan dipulihkan memakai token browser.
  socket.on("profile:load", (rawToken, callback = () => {}) => {
    let token = String(rawToken || "").trim();
    let profile = token ? profiles.get(token) : null;
    if (!profile) {
      token = crypto.randomBytes(32).toString("hex");
      profile = { token, name: "", totalPoints: 0, wins: 0, matches: 0, bestScore: 0, usedQuestions: [], updatedAt: Date.now() };
      profiles.set(token, profile);
      saveProfiles();
    }
    socket.data.profileToken = token;
    callback({ ok: true, token, name: profile.name, stats: {
      totalPoints: profile.totalPoints, wins: profile.wins, matches: profile.matches, bestScore: profile.bestScore
    }});
    socket.emit("leaderboard:update", leaderboardData());
  });

  socket.on("profile:set-name", (rawName, callback = () => {}) => {
    const profile = profiles.get(socket.data.profileToken);
    const name = String(rawName || "").trim().replace(/\s+/g, " ").slice(0, 16);
    if (!profile) return callback({ ok: false, message: "Profil belum siap. Muat ulang halaman." });
    if (name.length < 2) return callback({ ok: false, message: "Nama minimal 2 karakter." });
    profile.name = name;
    profile.updatedAt = Date.now();
    for (const room of rooms.values()) {
      const player = [...room.players.values()].find(item => item.profileToken === profile.token);
      if (player) {
        player.name = name;
        updateRoom(room);
      }
    }
    saveProfiles();
    callback({ ok: true, name: profile.name });
    publishLeaderboard();
  });

  socket.on("leaderboard:get", () => socket.emit("leaderboard:update", leaderboardData()));

  socket.on("resume-room", (callback = () => {}) => {
    const token = socket.data.profileToken;
    if (!token) return callback({ ok: false });
    for (const room of rooms.values()) {
      const entry = [...room.players.entries()].find(([, player]) => player.profileToken === token);
      if (!entry) continue;
      const [oldId, player] = entry;
      if (player.reconnectTimer) clearTimeout(player.reconnectTimer);
      room.players.delete(oldId);
      player.id = socket.id;
      player.connected = true;
      player.reconnectTimer = null;
      room.players.set(socket.id, player);
      if (room.host === oldId || !room.host) room.host = socket.id;
      socket.join(room.code);
      socket.data.roomCode = room.code;
      callback({ ok: true, code: room.code, state: publicRoom(room) });
      updateRoom(room);
      socket.emit("chat:message", { system: true, message: "Koneksi pulih. Kamu kembali ke arena!" });
      if (room.status === "playing") socket.emit("game:tick", room.seconds);
      if (room.status !== "playing" && room.status !== "finished" && !room.puzzle && !room.quizQuestion) room.status = "waiting";
      if (room.status === "finished" && (room.puzzle || room.quizQuestion || room.recorded)) socket.emit("game:finished");
      return;
    }
    callback({ ok: false });
  });

  socket.on("create-room", (data = {}, callback = () => {}) => {
    const profile = profiles.get(socket.data.profileToken);
    if (!profile?.name) return callback({ ok: false, message: "Simpan nama pemain terlebih dahulu." });
    removePlayer(socket);
    let code;
    do { code = makeCode(); } while (rooms.has(code));
    const room = {
      code, host: socket.id, status: "waiting", mode: data.mode === "meiquizz" ? "meiquizz" : "crossword", quizSettings: { matchType: data.quizSettings?.matchType === "duel" ? "duel" : "mixed", category: ["Campuran","Pengetahuan Umum","Matematika","Geografi","Sains","Teknologi","Olahraga","Sejarah","Alam & Lingkungan","Bahasa","Budaya & Seni"].includes(data.quizSettings?.category) ? data.quizSettings.category : "Campuran", difficulty: ["bertahap","mudah","sedang","sulit"].includes(data.quizSettings?.difficulty) ? data.quizSettings.difficulty : "bertahap" }, quizRound: 0, quizPhase: "points", quizQuestion: null, quizQuestionNumber: 0, usedQuizQuestions: new Set(), quizAnswered: new Set(), quizSurvivors: new Set(), players: new Map(),
      solved: new Set(), puzzle: null, seconds: GAME_DURATION, timer: null, recorded: false
    };
    room.players.set(socket.id, { id: socket.id, profileToken: profile.token, name: profile.name, score: 0, streak: 0, connected: true });
    rooms.set(code, room);
    socket.join(code);
    socket.data.roomCode = code;
    callback({ ok: true, code });
    updateRoom(room);
  });

  socket.on("join-room", (data = {}, callback = () => {}) => {
    const profile = profiles.get(socket.data.profileToken);
    const code = String(data.code || "").trim().toUpperCase();
    const room = rooms.get(code);
    if (!profile?.name) return callback({ ok: false, message: "Simpan nama pemain terlebih dahulu." });
    if (!room) return callback({ ok: false, message: "Room tidak ditemukan." });
    if (room.status !== "waiting") return callback({ ok: false, message: "Permainan sudah dimulai." });
    if (room.players.size >= MAX_PLAYERS) return callback({ ok: false, message: "Room sudah penuh (10 pemain)." });
    removePlayer(socket);
    room.players.set(socket.id, { id: socket.id, profileToken: profile.token, name: profile.name, score: 0, streak: 0, connected: true });
    socket.join(code);
    socket.data.roomCode = code;
    callback({ ok: true, code });
    updateRoom(room);
    io.to(code).emit("chat:message", { system: true, message: `${profile.name} bergabung ke arena.` });
  });

  socket.on("start-game", (code, callback = () => {}) => {
    const room = rooms.get(String(code || "").toUpperCase());
    if (!room) return callback({ ok: false, message: "Room tidak ditemukan." });
    if (room.host !== socket.id) return callback({ ok: false, message: "Hanya host yang bisa memulai." });
    const activeCount=[...room.players.values()].filter(player=>player.connected!==false).length;const requiredCount=room.mode==="meiquizz"?(room.quizSettings?.matchType==="duel"?2:10):MIN_PLAYERS;if(activeCount!==requiredCount)return callback({ok:false,message:`Mode ini membutuhkan tepat ${requiredCount} pemain aktif. Saat ini ${activeCount}.`});
    const ok = startGame(room);
    callback({ ok, message: ok ? "" : "Gagal memulai permainan." });
  });

  socket.on("meiquizz:answer", (data = {}, callback = () => {}) => {
    const room = rooms.get(String(data.room || "").toUpperCase());
    if (!room || room.mode !== "meiquizz" || room.status !== "playing") return callback({ ok:false, message:"Room MEIQUIZZ tidak aktif." });
    const player = room.players.get(socket.id); if (!player || player.eliminated) return callback({ok:false,message:"Kamu tidak aktif di ronde ini."});
    if (room.quizAnswered.has(socket.id)) return callback({ok:false,message:"Jawaban ronde ini sudah dikirim."});
    const q = room.quizQuestion; if (!q || String(data.questionId) !== q.id) return callback({ok:false,message:"Soal sudah berganti. Tunggu soal berikutnya."});
    room.quizAnswered.add(socket.id); const choice = Number(data.choice); const correct = choice === q.options.indexOf(q.answer);
    if (correct) { const points = room.quizPhase === "survival" ? 20 : 10 + Math.max(0, room.seconds); player.score += points; player.streak++; callback({ok:true,correct:true,points,explanation:q.explanation}); }
    else { player.streak=0; if(room.quizPhase === "survival") { player.eliminated=true; room.quizSurvivors.delete(socket.id); } callback({ok:true,correct:false,points:0,explanation:q.explanation,eliminated:room.quizPhase === "survival"}); }
    io.to(room.code).emit("meiquizz:answered", { playerId:socket.id, correct, eliminated:player.eliminated }); updateRoom(room);
    const eligible=[...room.players.values()].filter(p=>!p.eliminated && p.connected!==false);
    if (room.quizPhase === "survival" && eligible.length <= 1) return finishGame(room);
    if ([...room.players.values()].filter(p=>!p.eliminated && p.connected!==false).every(p=>room.quizAnswered.has(p.id))) advanceQuiz(room);
  });

  socket.on("submit-answer", (data = {}) => {
    const code = String(data.room || "").toUpperCase();
    const wordId = String(data.wordId || "");
    const answer = String(data.answer || "").trim().toUpperCase();
    const room = rooms.get(code);
    if (!room || room.status !== "playing") return;
    const player = room.players.get(socket.id);
    if (!player) return;
    const puzzleWord=(room.puzzle?.words||[]).find(w=>w.id===wordId);
    if (!puzzleWord) return socket.emit("answer:result", { ok: false, message: "Pertanyaan tidak valid." });
    if (room.solved.has(wordId)) return socket.emit("answer:result", { ok: false, message: "Kata ini sudah dijawab pemain lain." });
    if (answer !== puzzleWord.answer) {
      player.streak = 0;
      return socket.emit("answer:result", { ok: false, message: "Belum tepat. Coba lagi!" });
    }
    room.solved.add(wordId);
    player.streak += 1;
    const points = 10 + Math.min(player.streak - 1, 5) * 2;
    player.score += points;
    socket.emit("answer:result", { ok: true, points, message: `Benar! +${points} poin${player.streak > 1 ? ` · streak ${player.streak}x` : ""}.` });
    io.to(code).emit("game:announcement", { name: player.name, wordId, points });
    updateRoom(room);
    if (room.solved.size === (room.puzzle?.words.length || 0)) finishGame(room);
  });

  socket.on("chat:send", rawMessage => {
    const roomCode = socket.data.roomCode;
    const room = rooms.get(roomCode);
    const player = room?.players.get(socket.id);
    const now = Date.now();
    if (!room || !player || now - socket.data.lastChatAt < 700) return;
    const message = String(rawMessage || "").trim().slice(0, 120);
    if (!message) return;
    socket.data.lastChatAt = now;
    io.to(roomCode).emit("chat:message", { name: player.name, message, system: false });
  });

  socket.on("voice:status",active=>{const room=rooms.get(socket.data.roomCode),player=room?.players.get(socket.id);if(!room||!player)return;player.voiceActive=!!active;io.to(room.code).emit("voice:status",{id:socket.id,active:player.voiceActive});updateRoom(room);});
  for(const event of ["voice:offer","voice:answer","voice:ice"])socket.on(event,data=>{const room=rooms.get(socket.data.roomCode),to=String(data?.to||"");if(!room||!room.players.has(socket.id)||!room.players.has(to)||to===socket.id)return;io.to(to).emit(event,{...data,from:socket.id});});
  socket.on("voice:leave",()=>{const room=rooms.get(socket.data.roomCode);if(room)socket.to(room.code).emit("voice:leave",{id:socket.id});});
  socket.on("leave-room",()=>{const room=rooms.get(socket.data.roomCode);if(room)socket.to(room.code).emit("voice:leave",{id:socket.id});removePlayer(socket);});
  socket.on("disconnect",()=>{const room=rooms.get(socket.data.roomCode);if(room){const p=room.players.get(socket.id);if(p)p.voiceActive=false;socket.to(room.code).emit("voice:leave",{id:socket.id});}removePlayer(socket,true);});
});

server.listen(PORT, () => console.log(`ZIKRI WORD ARENA berjalan di port ${PORT}`));
