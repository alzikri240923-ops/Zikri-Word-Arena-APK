p="public/index.html"
s=open(p,encoding="utf-8").read()
js=r'''(function(){
  if(window.__zwaDiag) return; window.__zwaDiag=true;
  function desc(e){return e.tagName.toLowerCase()+(e.id?"#"+e.id:"")+(e.className&&typeof e.className==="string"?"."+e.className.trim().split(/\s+/).join("."):"");}
  function run(){
    var box=document.getElementById("zwaDiagBox");
    if(!box){
      box=document.createElement("div");
      box.id="zwaDiagBox";
      box.style.cssText="position:fixed;left:0;right:0;bottom:0;max-height:45%;overflow:auto;background:#000;color:#0f0;font:11px monospace;padding:6px;z-index:999999;white-space:pre-wrap;";
      document.body.appendChild(box);
    }
    var out=[];
    var all=document.querySelectorAll("body *");
    for(var i=0;i<all.length;i++){
      var el=all[i];
      if(el.id==="zwaDiagBox"||el.closest("#zwaDiagBox")) continue;
      if(el.children.length) continue;
      var t=(el.textContent||"").toLowerCase();
      if(t.indexOf("pesan dari developer")!==-1||t.indexOf("portofolio proyek")!==-1||t.indexOf("selamat datang kembali")!==-1){
        var chain=[];var n=el;
        while(n&&n.tagName!=="BODY"){chain.push(desc(n));n=n.parentElement;}
        out.push("["+t.slice(0,25)+"]\n"+chain.join("\n < "));
      }
    }
    box.textContent=out.join("\n\n")||"tidak ketemu";
  }
  setInterval(run,1500);
})();'''
lt=chr(60)
tag=lt+"script id=\"zwa-diag\">"+js+lt+"/script>"
bd=lt+"/body>"
if "zwa-diag" in s:
    print("SUDAH ADA")
else:
    i=s.rfind(bd)
    if i<0:
        print("BODY TIDAK KETEMU")
    else:
        open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
        print("DIAG_OK")
