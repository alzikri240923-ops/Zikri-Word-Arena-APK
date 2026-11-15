import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'style id="zwa-hidecss">.*?'+lt+'/style>',"",s,flags=re.S)
css=("#home.hidden,#home.hidden *{display:none !important;visibility:hidden !important;}"
     "body:has(#home.hidden) #zwaHomePortfolio,"
     "body:has(#home.hidden) #zwaBelowPortfolioGroup,"
     "body:has(#home.hidden) .zwa-home-portfolio,"
     "body:has(#home.hidden) .zwa-dev-quote-card{display:none !important;visibility:hidden !important;}")
tag=lt+'style id="zwa-hidecss">'+css+lt+'/style>'
i=s.rfind(lt+"/head>")
if i<0:
    print("HEAD TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
    print("HIDECSS2_OK")
