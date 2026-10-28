(function(){
  var el=document.getElementById("loc-map");
  var dataEl=document.getElementById("map-data");
  if(!el||!dataEl||el.getAttribute("data-map-ready")==="1") return;
  var points=[];
  try { points=JSON.parse(dataEl.textContent); } catch(e){ return; }
  var started=false;
  var cssHref="/vendor/leaflet/leaflet.css";
  var jsHref="/vendor/leaflet/leaflet.js";
  var cssSri="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H";
  var jsSri="sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH";
  function start(){
    if(started) return;
    started=true;
    var css=document.createElement("link");
    css.rel="stylesheet";
    css.href=cssHref;
    css.integrity=cssSri;
    css.crossOrigin="anonymous";
    css.onload=loadJs;
    css.onerror=loadJs;
    document.head.appendChild(css);
  }
  function loadJs(){
    if(window.L){ init(); return; }
    var s=document.createElement("script");
    s.src=jsHref;
    s.integrity=jsSri;
    s.crossOrigin="anonymous";
    s.onload=init;
    document.body.appendChild(s);
  }
  function init(){
    if(!window.L||el.getAttribute("data-map-ready")==="1") return;
    el.setAttribute("data-map-ready","1");
    var style=document.createElement("style");
    style.textContent=".leaflet-container{z-index:0;font-family:system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif}.leaflet-control-zoom-in,.leaflet-control-zoom-out{font-family:system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;font-size:1.25rem;font-weight:700;width:44px;height:44px;line-height:44px;color:#1C1915;background:#fff}.leaflet-popup-content{font-family:system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;font-size:1rem;line-height:1.55;color:#1C1915;margin:12px 16px}.leaflet-popup-content p{margin:12px 0 0}.leaflet-popup-content a{color:#083656}.leaflet-popup-content-wrapper,.leaflet-popup-tip{background:#fff;color:#1C1915}.leaflet-container a.leaflet-popup-close-button{color:#1C1915;width:24px;height:24px;font-size:1.25rem}.leaflet-control-attribution{background:#fff;color:#1C1915;font-size:0.875rem;line-height:1.4}.leaflet-control-attribution a{color:#083656}";
    document.head.appendChild(style);
    var label=el.getAttribute("data-label")||"Map of locations on this page";
    el.setAttribute("aria-label", label);
    el.textContent="";
    var map=L.map(el,{scrollWheelZoom:false,attributionControl:true,zoomControl:true,keyboard:true});
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{
      maxZoom:19,
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(map);
    var bounds=[];
    points.forEach(function(p){
      if(typeof p.lat!=="number"||typeof p.lon!=="number") return;
      var marker=L.marker([p.lat,p.lon],{alt:"Pin for "+p.name,title:p.name,keyboard:true});
      var box=document.createElement("div");
      var name=document.createElement("strong");
      name.textContent=p.name;
      box.appendChild(name);
      if(p.where){
        var where=document.createElement("p");
        where.textContent=p.where;
        box.appendChild(where);
      }
      if(p.directions){
        var para=document.createElement("p");
        var a=document.createElement("a");
        a.href=p.directions;
        a.target="_blank";
        a.rel="noopener";
        a.textContent="Get directions";
        para.appendChild(a);
        box.appendChild(para);
      }
      if(p.href){
        var backPara=document.createElement("p");
        var back=document.createElement("a");
        back.href=p.href;
        back.textContent="In the list on this page";
        backPara.appendChild(back);
        box.appendChild(backPara);
      }
      marker.bindPopup(box);
      marker.addTo(map);
      bounds.push([p.lat,p.lon]);
    });
    if(bounds.length===1) map.setView(bounds[0],14);
    else if(bounds.length) map.fitBounds(bounds,{padding:[24,24],maxZoom:14});
    map.scrollWheelZoom.disable();
    function armWheel(){ map.scrollWheelZoom.enable(); }
    map.on("click", armWheel);
    map.on("popupopen", armWheel);
    function disarmWheel(){
      if(!el.contains(document.activeElement)) map.scrollWheelZoom.disable();
    }
    el.addEventListener("mouseleave", disarmWheel);
    el.addEventListener("focusout", function(){ setTimeout(disarmWheel, 0); });
    map.whenReady(function(){ map.invalidateSize(); });
  }
  if(!("IntersectionObserver" in window)){ start(); return; }
  var io=new IntersectionObserver(function(entries){
    for(var i=0;i<entries.length;i++){
      if(entries[i].isIntersecting){ io.disconnect(); start(); break; }
    }
  },{rootMargin:"200px"});
  io.observe(el);
})();
