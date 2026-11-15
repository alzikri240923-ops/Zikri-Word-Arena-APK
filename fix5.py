import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
for sid in ("zwa-diag","zwa-purge","zwa-hidefix"):
    pat=lt+'script id="'+sid+'">.*?'+lt+'/script>'
    s=re.sub(pat,"",s,flags=re.S)
js=r'''(function(){
  if(window.__zwaHideFix) return; window.__zwaHideFix=true;
  var SEL=["#zwaHomePortfolio",".zwa-dev-quote-card"];
  function tick(){
    var home=document.getElementById("home");
    if(!home) return;
    var off=home.classList.contains("hidden");
    SEL.forEach(function(q){
      document.querySelectorAll(q).forEach(function(el){
        if(off) el.style.setProperty("display","none","important");
        else el.style.removeProperty("display");
      });
    });
  }
  setInterval(tick,300);
})();'''
tag=lt+'script id="zwa-hidefix">'+js+lt+'/script>'
bd=lt+"/body>"
i=s.rfind(bd)
if i<0:
    print("BODY TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
    print("HIDEFIX_OK")
