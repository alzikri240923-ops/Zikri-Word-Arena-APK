import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'script id="zwa-navfix">.*?'+lt+'/script>',"",s,flags=re.S)
js=r'''(function(){
  if(window.__zwaNavFix) return; window.__zwaNavFix=true;
  function tick(){
    var home=document.getElementById("home");
    var nav=document.getElementById("mainNav");
    if(!home||!nav) return;
    if(!home.classList.contains("hidden")){
      nav.classList.remove("hidden");
      nav.style.removeProperty("display");
    }
  }
  setInterval(tick,250);
})();'''
tag=lt+'script id="zwa-navfix">'+js+lt+'/script>'
b=s.rfind(lt+"/body>")
if b<0:
    print("BODY TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:b]+tag+s[b:])
    print("NAVFIX_OK")
