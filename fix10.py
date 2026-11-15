import re
p="public/index.html"
s=open(p,encoding="utf-8").read()
lt=chr(60)
s=re.sub(lt+'script id="zwa-misi-card">.*?'+lt+'/script>',"",s,flags=re.S)
js=r'''(function(){
  if(window.__zwaMisi) return; window.__zwaMisi=true;
  var cur="home", prev="home";
  function wrap(){
    if(typeof window.openPage!=="function"||window.openPage.__zn) return;
    var o=window.openPage;
    var w=function(id){
      if(id && id!==cur){ prev=cur; cur=id; }
      return o.apply(this,arguments);
    };
    w.__zn=true; w.__hooked=o.__hooked;
    window.openPage=w;
  }
  function mk(t,c,x){var e=document.createElement(t); if(c) e.className=c; if(x) e.textContent=x; return e;}
  function build(){
    var sec=document.getElementById("achievements");
    if(!sec || document.getElementById("zwaMisiCard")) return;
    var card=mk("div","zwa-misi-card"); card.id="zwaMisiCard";
    card.appendChild(mk("div","zwa-misi-icon","🏆"));
    card.appendChild(mk("div","zwa-misi-badge","COMING SOON"));
    card.appendChild(mk("h2","zwa-misi-title","Misi Segera Hadir"));
    card.appendChild(mk("p","zwa-misi-desc","Fitur misi sedang dibersihkan dan disiapkan ulang. Hadiah Diamond untuk misi akan hadir di pembaruan berikutnya."));
    var bar=mk("div","zwa-misi-bar"); bar.appendChild(mk("span")); card.appendChild(bar);
    var row=mk("div","zwa-misi-chips");
    ["💎 Hadiah Diamond","🏅 Achievement"].forEach(function(t){row.appendChild(mk("span","zwa-misi-chip",t));});
    card.appendChild(row);
    var btn=mk("button","btn btn-secondary zwa-misi-back","← Kembali");
    btn.type="button";
    btn.onclick=function(){
      var t=(prev && prev!=="achievements") ? prev : "home";
      if(typeof window.openPage==="function") window.openPage(t);
    };
    card.appendChild(btn);
    sec.insertBefore(card,sec.firstChild);
  }
  setInterval(function(){ wrap(); build(); },500);
})();'''
script=lt+'script id="zwa-misi-card">'+js+lt+'/script>'
b=s.rfind(lt+"/body>")
if b<0:
    print("BODY TIDAK KETEMU")
else:
    open(p,"w",encoding="utf-8").write(s[:b]+script+s[b:])
    print("BACK_OK")
