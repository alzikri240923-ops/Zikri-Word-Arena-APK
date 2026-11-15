import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'style id="zwa-misi-css">.*?'+lt+'/style>',"",s,flags=re.S)
css=("#achievements .menu-title{margin:0 0 4px}"
"#achievements .menu-desc{margin:0 0 16px;opacity:.8;line-height:1.5}"
"#achievements .menu-kpi{display:grid !important;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}"
"#achievements .stat{text-align:center;padding:12px 6px;border-radius:14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1)}"
"#achievements .stat strong{display:block;font-size:22px;color:#f6d98a}"
"#achievements .stat span{display:block;font-size:11px;opacity:.75;margin-top:2px}"
"#achievements .achievement-list{display:grid;grid-template-columns:1fr;gap:10px}"
"#achievements .achievement-list>*{padding:14px;border-radius:14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1)}")
tag=lt+'style id="zwa-misi-css">'+css+lt+'/style>'
i=s.rfind(lt+"/head>")
if i<0:
    print("HEAD TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:i]+tag+s[i:])
    print("MISI_CSS_OK")
