import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
for i in ("zwa-remember","zwa-remember2","zwa-startfix"):
    s=re.sub(lt+'script id="'+i+'">.*?'+lt+'/script>',"",s,flags=re.S)
js=r'''(function(){
  var KEY="zwa_last_page";
  var RX=/menu/i;
  var MENU=["profile","modes","achievements","ranking","help","settings","shop","cwMenu","mqSetup"];
  var GAME=["lobby","game","meiquizz","result"];
  var ALL=["home"].concat(MENU,GAME);
  try{sessionStorage.clear();}catch(e){}
  try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k&&RX.test(k))localStorage.removeItem(k);}}catch(e){}
  try{
    var sp=Storage.prototype,gi=sp.getItem,si=sp.setItem;
    sp.getItem=function(k){if(RX.test(String(k)))return null;return gi.apply(this,arguments);};
    sp.setItem=function(k,v){if(RX.test(String(k)))return;return si.apply(this,arguments);};
  }catch(e){}
  try{
    var rs=history.replaceState;
    history.replaceState=function(a,b,u){if(u&&/zwa_menu/i.test(String(u)))return;return rs.apply(this,arguments);};
    if(location.hash)rs.call(history,null,"",location.pathname+location.search);
  }catch(e){}
  function vis(id){
    var e=document.getElementById(id);
    if(!e||e.classList.contains("hidden"))return false;
    return getComputedStyle(e).display!=="none";
  }
  function current(){
    for(var i=1;i<ALL.length;i++){if(vis(ALL[i]))return ALL[i];}
    return vis("home")?"home":null;
  }
  var saved=null;
  try{saved=localStorage.getItem(KEY);}catch(e){}
  var target=saved;
  if(target&&GAME.indexOf(target)!==-1)target="modes";
  var locked=true,t0=Date.now();
  ["pointerdown","touchstart","mousedown","keydown"].forEach(function(ev){
    window.addEventListener(ev,function(){if(locked&&Date.now()-t0>600)locked=false;},true);
  });
  setInterval(function(){
    var age=Date.now()-t0;
    if(locked){
      if(!target||target==="home"){if(age>1500)locked=false;return;}
      if(typeof window.openPage==="function"&&current()!==target){
        try{window.openPage(target);}catch(e){}
      }
      if(age>4000)locked=false;
      return;
    }
    var c=current();
    if(c){try{localStorage.setItem(KEY,c);}catch(e){}}
  },250);
})();'''
tag=lt+'script id="zwa-remember2">'+js+lt+'/script>'
m=re.search(lt+r'head[^>]*>',s)
if not m:
    print("HEAD TIDAK KETEMU")
else:
    s=s[:m.end()]+tag+s[m.end():]
    open(p,"w",encoding="utf-8").write(s)
    print("REMEMBER2_OK")
