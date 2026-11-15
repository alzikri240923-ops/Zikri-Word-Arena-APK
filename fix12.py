import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'script id="zwa-persist">.*?'+lt+'/script>',"",s,flags=re.S)
s=re.sub(lt+'script id="zwa-startfix">.*?'+lt+'/script>',"",s,flags=re.S)
js=r'''(function(){
  try{["zwa_active_page","zwa_p","zwa_lp"].forEach(function(k){sessionStorage.removeItem(k);});}catch(e){}
  try{if(location.hash){history.replaceState(null,"",location.pathname+location.search);}}catch(e){}
})();'''
tag=lt+'script id="zwa-startfix">'+js+lt+'/script>'
m=re.search(lt+r'head[^>]*>',s)
if not m:
    print("HEAD TIDAK KETEMU")
else:
    s=s[:m.end()]+tag+s[m.end():]
    open(p,"w",encoding="utf-8").write(s)
    print("STARTFIX_OK")
