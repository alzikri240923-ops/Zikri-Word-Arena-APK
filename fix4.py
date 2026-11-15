p="public/index.html"
s=open(p,encoding="utf-8").read()
js=r'''(function(){
  if(window.__zwaPurge) return; window.__zwaPurge=true;
  var KEYS=["selamat datang kembali","portofolio","pesan dari developer"];
  function purge(){
    var home=document.getElementById("home");
    var hero=document.getElementById("hero");
    if(!home || !home.classList.contains("hidden")) return;
    var nodes=document.querySelectorAll("body div, body aside, body article, body p");
    nodes.forEach(function(el){
      if(!el.isConnected) return;
      if(home.contains(el) || (hero && hero.contains(el))) return;
      if(el.closest("#mainNav") || el.closest("section[id]")) return;
      if(el.querySelector("section[id]")) return;
      var t=(el.textContent||"").toLowerCase();
      if(t.length>1500) return;
      if(KEYS.some(function(k){return t.indexOf(k)!==-1;})) el.remove();
    });
  }
  setInterval(purge,500);
})();'''
lt=chr(60)
tag=lt+"script id=\"zwa-purge\">"+js+lt+"/script>"
bd=lt+"/body>"
if "zwa-purge" in s:
    print("SUDAH ADA")
else:
    i=s.rfind(bd)
    if i<0:
        print("BODY TIDAK KETEMU")
    else:
        open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
        print("PATCHED_PURGE")
