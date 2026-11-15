p="public/index.html"
s=open(p,encoding="utf-8").read()
patch=''''''
if "zwa-purge" in s:
    print("SUDAH ADA")
else:
    i=s.rfind("")
    open(p,"w",encoding="utf-8").write(s[:i]+patch+s[i:])
    print("PATCHED_PURGE")
