(function(){
  var el=document.getElementById("search-data");
  var input=document.getElementById("q");
  var box=document.getElementById("search-results");
  if(!el||!input||!box) return;
  var pages=[];
  try { pages=JSON.parse(el.textContent); } catch(e){ return; }
  function esc(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];
    });
  }
  function activeWords(q){
    var t=String(q||"").trim().toLowerCase();
    if(t.length<2) return [];
    return t.split(/\s+/).filter(function(w){ return w; });
  }
  function match(blob, ws){
    if(!ws.length) return true;
    blob=String(blob).toLowerCase();
    for(var i=0;i<ws.length;i++) if(blob.indexOf(ws[i])<0) return false;
    return true;
  }
  function filterIndex(q){
    var lists=document.querySelectorAll("ul.topic-list");
    if(!lists.length) return;
    var ws=activeWords(q);
    var shown=0;
    var total=0;
    for(var i=0;i<lists.length;i++){
      var list=lists[i];
      var items=list.querySelectorAll("li");
      var any=false;
      for(var k=0;k<items.length;k++){
        var li=items[k];
        total++;
        var blob=li.textContent+" "+(li.getAttribute("data-keywords")||"");
        var ok=match(blob, ws);
        li.hidden=!ok;
        if(ok){ any=true; shown++; }
      }
      list.hidden=!any;
      var h2=list.previousElementSibling;
      if(h2&&h2.tagName==="H2") h2.hidden=!any;
    }
    var status=document.getElementById("index-status");
    if(status){
      if(!ws.length) status.textContent="Showing every page.";
      else if(!shown) status.textContent="No page matches. Try a different word, or clear the search.";
      else status.textContent="Showing "+shown+" of "+total+" pages.";
    }
  }
  function show(q){
    var ws=activeWords(q);
    if(!ws.length){
      box.hidden=true;
      box.innerHTML="";
    } else {
      var hits=[];
      for(var i=0;i<pages.length;i++){
        var p=pages[i];
        var blob=p.t+" "+p.s+" "+p.g+" "+(p.k||"");
        if(match(blob, ws)) hits.push(p);
      }
      if(!hits.length){
        box.innerHTML="<p class=\"search-empty\">No matching page. Open the <a href=\"/find/\">full page list</a>.</p>";
      } else {
        var html="<ul>";
        var n=Math.min(8, hits.length);
        for(var j=0;j<n;j++){
          var hit=hits[j];
          html+="<li><a href=\""+esc(hit.u)+"\"><strong>"+esc(hit.t)+"</strong><span>"+esc(hit.s)+"</span></a></li>";
        }
        if(hits.length>8){
          var more="/find/?q="+encodeURIComponent(String(q||"").trim());
          html+="<li><a href=\""+esc(more)+"\"><strong>All "+hits.length+" matching pages</strong><span>Open the full page list.</span></a></li>";
        }
        html+="</ul>";
        box.innerHTML=html;
      }
      box.hidden=false;
    }
    filterIndex(q);
  }
  input.addEventListener("input", function(){ show(input.value); });
  input.addEventListener("keydown", function(e){
    if(e.key==="Escape"){ box.hidden=true; box.innerHTML=""; }
  });
  document.addEventListener("click", function(e){
    if(!box.contains(e.target) && e.target!==input){ box.hidden=true; }
  });
  var initial="";
  try { initial=new URLSearchParams(window.location.search).get("q")||""; } catch(err){ initial=""; }
  if(initial){ input.value=initial; show(initial); }
  else filterIndex("");
})();
(function(){
  var header=document.getElementById("site-header");
  var slot=document.getElementById("head-slot");
  var toggle=document.querySelector(".search-toggle");
  var search=document.getElementById("site-search");
  var nav=document.getElementById("site-nav");
  if(!header||!slot) return;
  var docked=false;
  var fullH=0;
  var compactH=0;
  function setSearchOpen(open){
    if(!search||!toggle) return;
    if(open && !document.body.classList.contains("is-docked")) open=false;
    search.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open?"true":"false");
    if(open){
      closeGroups();
      var input=document.getElementById("q");
      if(input) input.focus();
    }
  }
  function closeGroups(){
    var open=document.querySelectorAll(".grp[open]");
    for(var i=0;i<open.length;i++) open[i].removeAttribute("open");
    if(nav) nav.classList.remove("menu-open");
  }
  function setPanelTop(){
    document.documentElement.style.setProperty("--panel-top", header.getBoundingClientRect().bottom+"px");
  }
  function applyPad(){
    var h=compactH||header.getBoundingClientRect().height;
    var pad=Math.ceil(h+12);
    document.documentElement.style.setProperty("--scroll-pad", pad+"px");
    setPanelTop();
  }
  function measure(){
    if(docked) return;
    if(document.querySelector(".grp[open]")) return;
    fullH=header.offsetHeight;
  }
  function measureCompact(){
    var was=document.body.classList.contains("is-docked");
    document.body.classList.add("is-docked");
    var h=header.offsetHeight;
    if(!was) document.body.classList.remove("is-docked");
    return h;
  }
  function updateHint(){
    if(!nav) return;
    var more=nav.scrollWidth>nav.clientWidth+8;
    var atEnd=nav.scrollLeft+nav.clientWidth>=nav.scrollWidth-8;
    var atStart=nav.scrollLeft<=8;
    document.body.classList.toggle("nav-more-right", !!(more && !atEnd));
    document.body.classList.toggle("nav-more-left", !!(more && !atStart));
  }
  function revealCurrent(){
    if(!nav) return;
    var cur=nav.querySelector(".grp.has-current");
    if(!cur || nav.scrollWidth<=nav.clientWidth+8){ updateHint(); return; }
    var left=cur.offsetLeft-(nav.clientWidth-cur.offsetWidth)/2;
    nav.scrollLeft=left<0?0:left;
    updateHint();
  }
  function dock(){
    if(docked) return;
    closeGroups();
    setSearchOpen(false);
    measure();
    if(!fullH) fullH=header.offsetHeight;
    slot.style.height=fullH+"px";
    document.body.classList.add("is-docked");
    docked=true;
    compactH=header.offsetHeight;
    applyPad();
    revealCurrent();
  }
  function undock(){
    if(!docked) return;
    setSearchOpen(false);
    closeGroups();
    document.body.classList.remove("is-docked");
    document.body.classList.remove("nav-more-right");
    document.body.classList.remove("nav-more-left");
    slot.style.height="";
    docked=false;
    measure();
    applyPad();
  }
  function onScroll(){
    var y=window.scrollY||document.documentElement.scrollTop||0;
    if(!fullH) measure();
    var line=Math.max(24, fullH-compactH);
    if(!docked){
      measure();
      if(fullH>compactH+8 && y>line) dock();
    } else if(y<line-24){
      undock();
    }
    setPanelTop();
  }
  if(toggle){
    toggle.addEventListener("click", function(){
      var open=toggle.getAttribute("aria-expanded")==="true";
      setSearchOpen(!open);
    });
  }
  if(nav){
    var sums=nav.querySelectorAll(".grp>summary");
    for(var s=0;s<sums.length;s++){
      sums[s].addEventListener("click", function(){
        setSearchOpen(false);
        var parent=this.parentNode;
        var open=document.querySelectorAll(".grp[open]");
        for(var i=0;i<open.length;i++) if(open[i]!==parent) open[i].removeAttribute("open");
      });
    }
    nav.addEventListener("toggle", function(e){
      var any=nav.querySelector(".grp[open]");
      nav.classList.toggle("menu-open", !!any);
      setPanelTop();
    }, true);
    nav.addEventListener("scroll", updateHint, {passive:true});
  }
  document.addEventListener("keydown", function(e){
    if(e.key!=="Escape") return;
    setSearchOpen(false);
    closeGroups();
    var box=document.getElementById("search-results");
    if(box){ box.hidden=true; box.innerHTML=""; }
  });
  document.addEventListener("click", function(e){
    if(header.contains(e.target)) return;
    setSearchOpen(false);
    closeGroups();
  });
  document.addEventListener("focusin", function(e){
    var t=e.target;
    if(!t||!docked) return;
    if(nav && nav.contains(t) && nav.scrollWidth>nav.clientWidth+8 && t.closest){
      var grp=t.closest(".grp");
      if(grp){
        var pad=16;
        var left=grp.offsetLeft-pad;
        var right=grp.offsetLeft+grp.offsetWidth+pad;
        if(left<nav.scrollLeft) nav.scrollLeft=Math.max(0,left);
        else if(right>nav.scrollLeft+nav.clientWidth) nav.scrollLeft=right-nav.clientWidth;
        updateHint();
      }
    }
    if(header.contains(t)||(t.classList&&t.classList.contains("skip"))) return;
    var edge=header.getBoundingClientRect().bottom+12;
    var r=t.getBoundingClientRect();
    if(r.top>=edge) return;
    var y=(window.scrollY||0)+r.top-edge;
    window.scrollTo(0, y<0?0:y);
  });
  window.addEventListener("scroll", onScroll, {passive:true});
  window.addEventListener("resize", function(){
    if(docked) undock();
    measure();
    compactH=measureCompact();
    applyPad();
    onScroll();
    updateHint();
  });
  measure();
  compactH=measureCompact();
  applyPad();
  onScroll();
  updateHint();
  if(location.hash){
    var id="";
    try { id=decodeURIComponent(location.hash.slice(1)); } catch(err){ id=location.hash.slice(1); }
    var target=id&&document.getElementById(id);
    if(target && target.scrollIntoView) target.scrollIntoView();
  }
})();
