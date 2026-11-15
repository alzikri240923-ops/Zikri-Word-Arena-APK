p="public/index.html"
s=open(p,encoding="utf-8").read()
patch='''<script id="zwa-fixhome">
(function(){
  if(window.__zwaFixHome) return; window.__zwaFixHome=true;
  const KEYS=["selamat datang di zikri","portofolio proyek","portofolio · zikri","a place to think"];
  const has=el=>KEYS.some(k=>(el.textContent||"").toLowerCase().includes(k));
  function apply(){
    const home=document.getElementById("home");
    if(!home) return;
    const container=home.parentElement;
    const isHome=!home.classList.contains("hidden");
    document.querySelectorAll("body *").forEach(el=>{
      if(["SCRIPT","STYLE"].includes(el.tagName)||!has(el)) return;
      if(Array.from(el.children).some(has)) return;
      let n=el;
      while(n.parentElement && n.parentElement!==container && n.parentElement.tagName!=="SECTION"){ n=n.parentElement; }
      if(n.tagName==="SECTION" && n.id) return;
      if(isHome) n.style.removeProperty("display");
      else n.style.setProperty("display","none","important");
    });
  }
  function wrap(){
    if(typeof window.openPage!=="function"||window.openPage.__fh) return;
    const o=window.openPage;
    window.openPage=function(){
      let r;
      try{ r=o.apply(this,arguments); } finally {
        apply(); setTimeout(apply,150); setTimeout(apply,600);
      }
      return r;
    };
    window.openPage.__fh=true;
  }
  window.addEventListener("load",()=>{ setTimeout(wrap,400); });
})();
</script>'''
if "zwa-fixhome" in s:
    print("SUDAH ADA")
else:
    i=s.rfind("</body>")
    open(p,"w",encoding="utf-8").write(s[:i]+patch+s[i:])
    print("FIXED2")
