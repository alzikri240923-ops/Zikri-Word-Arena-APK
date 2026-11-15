import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'script id="zwa-startfix">.*?'+lt+'/script>',"",s,flags=re.S)
for tg,i in (("script","zwa-navfix"),("script","zwa-misi-card"),("style","zwa-misi-css"),("style","zwa-hidecss")):
    pat=re.compile(lt+tg+' id="'+i+'">.*?'+lt+'/'+tg+'>',re.S)
    ms=list(pat.finditer(s))
    for m in reversed(ms[:-1]):
        s=s[:m.start()]+s[m.end():]
    print(i,"ditemukan",len(ms),"-> sisa",min(len(ms),1))
js=r'''(function(){
  var RX=/menu/i;
  try{sessionStorage.clear();}catch(e){}
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
})();'''
tag=lt+'script id="zwa-startfix">'+js+lt+'/script>'
m=re.search(lt+r'head[^>]*>',s)
if not m:
    print("HEAD TIDAK KETEMU")
else:
    s=s[:m.end()]+tag+s[m.end():]
    open(p,"w",encoding="utf-8").write(s)
    print("STARTFIX2_OK")
