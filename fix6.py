import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
for sid in ("zwa-hidefix","zwa-hidecss"):
    s=re.sub(lt+'script id="'+sid+'">.*?'+lt+'/script>',"",s,flags=re.S)
    s=re.sub(lt+'style id="'+sid+'">.*?'+lt+'/style>',"",s,flags=re.S)
css="#home.hidden #zwaHomePortfolio,#home.hidden .zwa-dev-quote-card,#home.hidden .zwa-home-portfolio{display:none !important;visibility:hidden !important;}"
tag=lt+'style id="zwa-hidecss">'+css+lt+'/style>'
bd=lt+"/head>"
i=s.rfind(bd)
if i<0:
    print("HEAD TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
    print("HIDECSS_OK")
