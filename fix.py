p="public/index.html"
s=open(p,encoding="utf-8").read()
old='$("hero").classList.toggle("hidden",id!=="home");'
new=old+'["zwaHeroTcc","zwaHomePortfolio","zwaBelowPortfolioGroup"].forEach(k=>{const e=document.getElementById(k);if(e){if(id==="home")e.style.removeProperty("display");else e.style.setProperty("display","none","important");}});'
if s.count(old)==1:
    open(p,"w",encoding="utf-8").write(s.replace(old,new,1))
    print("FIXED")
else:
    print("COUNT",s.count(old))
