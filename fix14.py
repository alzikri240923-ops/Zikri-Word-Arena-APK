import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
for i in ("zwa-startfix","zwa-remember"):
    s=re.sub(lt+'script id="'+i+'">.*?'+lt+'/script>',"",s,flags=re.S)
js=r'''(function(){
  var KEY="zwa_last_page";
  var PAGES=["profile","modes","achievements","ranking","help","shop","settings"];
  var RX=/menu/i;
  try{ sessionStorage.removeItem("zwa_active_page"); }catch(e){}
  try{
    for(var i=localStorage.length-1;i>=0;i--){
      var k=localStorage.key(i);
      if(k&&RX.test(k)) localStorage.removeItem(k);
    }
  }catch(e){}
  try{
    var sp=Storage.prototype, gi=sp.getItem, si=sp.setItem;
    sp.getItem=function(k){ if(RX.test(String(k))) return null; return gi.apply(this,arguments); };
    sp.setItem=function(k,v){ if(RX.test(String(k))) return; return si.apply(this,arguments); };
  }catch(e){}
  try{
    var rs=history.replaceState;
    history.replaceState=function(a,b,u){ if(u && /zwa_menu/i.test(String(u))) return; return rs.apply(this,arguments); };
    if(location.hash){ rs.call(history,null,"",location.pathname+location.search); }
  }catch(e){}
  var current=null;
  function save(id){
    try{
      if(PAGES.indexOf(id)!==-1) localStorage.setItem(KEY,id);
      else if(id==="home") localStorage.removeItem(KEY);
    }catch(e){}
  }
  function wrap(){
    if(typeof window.openPage!=="function"||window.openPage.__rm) return;
    var o=window.openPage;
    var w=function(id){
      var r=o.apply(this,arguments);
      current=id; save(id);
      return r;
    };
    w.__rm=true; w.__hooked=o.__hooked;
    window.openPage=w;
  }
  var restored=false;
  function restore(){
    if(restored) return;
    if(typeof window.openPage!=="function") return;
    restored=true;
    var id=null;
    try{ id=localStorage.getItem(KEY); }catch(e){}
    if(id && PAGES.indexOf(id)!==-1){
      [0,300,900,1800].forEach(function(ms){
        setTimeout(function(){ try{ window.openPage(id); }catch(e){} },ms);
      });
    }
  }
  var n=0;
  var t=setInterval(function(){
    wrap();
    if(window.openPage && window.openPage.__rm){ restore(); }
    if(++n>40) clearInterval(t);
  },150);
})();'''
tag=lt+'script id="zwa-remember">'+js+lt+'/script>'
m=re.search(lt+r'head[^>]*>',s)
if not m:
    print("HEAD TIDAK KETEMU")
else:
    s=s[:m.end()]+tag+s[m.end():]
    open(p,"w",encoding="utf-8").write(s)
    print("REMEMBER_OK")
