import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
for sid,tg in (("zwa-misi-css","style"),("zwa-misi-card","script")):
    s=re.sub(lt+tg+' id="'+sid+'">.*?'+lt+'/'+tg+'>',"",s,flags=re.S)
css=r'''#achievements>*:not(#zwaMisiCard){display:none !important}
#achievements{min-height:0 !important;height:auto !important}
#zwaMisiCard{position:relative;text-align:center;padding:30px 18px 22px;border-radius:22px;background:linear-gradient(160deg,rgba(246,217,138,.10),rgba(255,255,255,.03));border:1px solid rgba(246,217,138,.35);box-shadow:0 14px 40px rgba(0,0,0,.35),0 0 28px rgba(246,217,138,.12);overflow:hidden;animation:zwaMisiIn .6s ease both}
#zwaMisiCard::before{content:"";position:absolute;top:0;left:-60%;width:40%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.10),transparent);animation:zwaMisiSheen 4.5s ease-in-out infinite;pointer-events:none}
.zwa-misi-icon{font-size:56px;line-height:1;animation:zwaMisiFloat 3s ease-in-out infinite;filter:drop-shadow(0 6px 14px rgba(246,217,138,.45))}
.zwa-misi-badge{display:inline-block;margin:14px 0 8px;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:800;letter-spacing:.18em;color:#f6d98a;background:rgba(246,217,138,.12);border:1px solid rgba(246,217,138,.4);animation:zwaMisiPulse 2.2s ease-in-out infinite}
.zwa-misi-title{margin:0 0 8px;font-size:22px}
.zwa-misi-desc{margin:0 auto 18px;max-width:34ch;line-height:1.6;opacity:.8;font-size:14px}
.zwa-misi-bar{height:8px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;margin:0 auto 18px;max-width:260px}
.zwa-misi-bar span{display:block;height:100%;width:45%;border-radius:99px;background:linear-gradient(90deg,#f6d98a,#e9a93b,#f6d98a);background-size:200% 100%;animation:zwaMisiBar 2s linear infinite}
.zwa-misi-chips{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:20px}
.zwa-misi-chip{padding:6px 12px;border-radius:999px;font-size:12px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12)}
.zwa-misi-back{width:100%;transition:transform .15s ease}
.zwa-misi-back:active{transform:scale(.97)}
@keyframes zwaMisiIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes zwaMisiSheen{0%{left:-60%}60%,100%{left:130%}}
@keyframes zwaMisiFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes zwaMisiPulse{0%,100%{box-shadow:0 0 0 0 rgba(246,217,138,.35)}50%{box-shadow:0 0 0 8px rgba(246,217,138,0)}}
@keyframes zwaMisiBar{from{background-position:0 0}to{background-position:200% 0}}'''
js=r'''(function(){
  if(window.__zwaMisi) return; window.__zwaMisi=true;
  function mk(t,c,x){var e=document.createElement(t); if(c) e.className=c; if(x) e.textContent=x; return e;}
  function build(){
    var sec=document.getElementById("achievements");
    if(!sec || document.getElementById("zwaMisiCard")) return;
    var card=mk("div","zwa-misi-card"); card.id="zwaMisiCard";
    card.appendChild(mk("div","zwa-misi-icon","🏆"));
    card.appendChild(mk("div","zwa-misi-badge","COMING SOON"));
    card.appendChild(mk("h2","zwa-misi-title","Misi Segera Hadir"));
    card.appendChild(mk("p","zwa-misi-desc","Fitur misi sedang dibersihkan dan disiapkan ulang. Hadiah Diamond untuk misi akan hadir di pembaruan berikutnya."));
    var bar=mk("div","zwa-misi-bar"); bar.appendChild(mk("span")); card.appendChild(bar);
    var row=mk("div","zwa-misi-chips");
    ["💎 Hadiah Diamond","🏅 Achievement"].forEach(function(t){row.appendChild(mk("span","zwa-misi-chip",t));});
    card.appendChild(row);
    var btn=mk("button","btn btn-secondary zwa-misi-back","← Kembali ke Menu");
    btn.type="button";
    btn.onclick=function(){ if(typeof window.openPage==="function") window.openPage("home"); };
    card.appendChild(btn);
    sec.insertBefore(card,sec.firstChild);
  }
  setInterval(build,500);
})();'''
style=lt+'style id="zwa-misi-css">'+css+lt+'/style>'
script=lt+'script id="zwa-misi-card">'+js+lt+'/script>'
h=s.rfind(lt+"/head>")
b=s.rfind(lt+"/body>")
if h<0 or b<0:
    print("TAG TIDAK KETEMU")
else:
    s=s[:b]+script+s[b:]
    s=s[:h]+style+s[h:]
    open(p,"w",encoding="utf-8").write(s)
    print("MISI_UI_OK")
