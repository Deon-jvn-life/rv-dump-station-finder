#!/usr/bin/env python3
"""Build the Florida RV dump stations static site from JSON in tools/ into site/."""
import json,os,re,html as H,shutil,sys,struct,zlib,urllib.parse
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,'site')
D="26 October 2026"; SP="27 October 2026"; BASE="https://rv-dump-station-finder.vercel.app"  # replace with real domain before deploy
# Optional search-console tokens. A blank value omits that meta tag.
VERIFY={"google-site-verification":"XA7XgB_UwrIRvQyNVsnWpSyTyaU6e3-v4g4RBw8RAVI","msvalidate.01":""}
DISCLAIMER="For general information only. This independent site is not affiliated with any government or agency. Information can change and may contain errors; always confirm with the official source or facility before you act. Nothing here is legal or professional advice, and we accept no liability for decisions made using it."
NEW="26 October 2026"
S=dict(fsp="https://www.floridastateparks.org/stay-night",fdot="https://www.fdot.gov/maintenance/rest-area-app/restareainfo.shtm",
 fdotlist="https://www.fdot.gov/maintenance/rest-area-app/rest-facilities-list",osm="https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dsanitary_dump_station",
 osmc="https://www.openstreetmap.org/copyright",overpass="https://overpass-api.de/",fspres="https://www.floridastateparks.org/stay-night",
 rainbow="https://www.floridastateparks.org/parks-and-trails/rainbow-springs-state-park/experiences-amenities",
 anastasia="https://www.floridastateparks.org/parks-and-trails/anastasia-state-park/experiences-amenities",loves="https://www.loves.com/location-and-fuel-price-search",
 s51308="https://www.flsenate.gov/Laws/Statutes/2026/0513.08",s51301="https://www.flsenate.gov/Laws/Statutes/2026/0513.01",
 s403413="https://www.flsenate.gov/Laws/Statutes/2026/403.413",s403161="https://www.flsenate.gov/Laws/Statutes/2026/0403.161",
 s38601="https://www.flsenate.gov/Laws/Statutes/2026/0386.01",s386041="https://www.flsenate.gov/Laws/Statutes/2026/0386.041",
 s386051="https://www.flsenate.gov/Laws/Statutes/2026/0386.051",s775082="https://www.flsenate.gov/Laws/Statutes/2026/0775.082",
 s775083="https://www.flsenate.gov/Laws/Statutes/2026/0775.083",
 r64e15001="https://flrules.org/gateway/ruleNo.asp?id=64E-15.001",r64e15004="https://flrules.org/gateway/ruleNo.asp?id=64E-15.004",
 r64e15005="https://flrules.org/gateway/ruleNo.asp?id=64E-15.005",
 r64e15pdf="https://glades.floridahealth.gov/wp-content/uploads/sites/23/2025/05/64e-15.pdf",
 c64e6="https://flrules.org/gateway/ChapterHome.asp?Chapter=64E-6",
 r64e6001="https://flrules.org/gateway/RuleNo.asp?ID=64E-6.001",
 c626="https://flrules.org/gateway/ChapterHome.asp?Chapter=62-6",
 c62600="https://flrules.org/gateway/ChapterHome.asp?Chapter=62-600",
 r1428="https://flrules.org/gateway/ruleNo.asp?id=14-28.002",
 r1428pdf="https://fdotwww.blob.core.windows.net/sitefinity/docs/default-source/maintenance/cont/ra/14-28-002.pdf",
 fdotgis="https://gis.fdot.gov/arcgis/rest/services/fdotRestFacilities/MapServer/1",
 s258014="https://www.flsenate.gov/Laws/Statutes/2026/0258.014",
 fspfee="https://www.floridastateparks.org/sites/default/files/media/file/2021_05_10%20FSP%20Fee%20Schedule.pdf",
 fspfee2="https://www.floridastateparks.org/sites/default/files/inline-files/2021_05_10%20FSP%20Fee%20Schedule%2005.2022.pdf",
 fspfee2013="https://www.floridastateparks.org/sites/default/files/inline-files/2013_10_01%20Fee%20Schedule%20-%20NEW%20FORMAT.pdf",
 fspcamp="https://www.floridastateparks.org/camping",
 fspfaq="https://www.floridastateparks.org/plan-your-visit/faqs",
 koreshan="https://www.floridastateparks.org/parks-and-trails/koreshan-state-park/hours-fees",
 oscar="https://www.floridastateparks.org/parks-and-trails/oscar-scherer-state-park/hours-fees",
 bluespring="https://www.floridastateparks.org/parks-and-trails/blue-spring-state-park/experiences-amenities",
 bluespringh="https://www.floridastateparks.org/parks-and-trails/blue-spring-state-park/hours-fees",
 fortclinch="https://www.floridastateparks.org/parks-and-trails/fort-clinch-state-park/experiences-amenities-0",
 fortclinchh="https://www.floridastateparks.org/parks-and-trails/fort-clinch-state-park/hours-fees",
 anastasiah="https://www.floridastateparks.org/parks-and-trails/anastasia-state-park/hours-fees",
 gamble="https://www.floridastateparks.org/parks-and-trails/gamble-rogers-memorial-state-recreation-area-flagler-beach/experiences-amenities",
 gambleh="https://www.floridastateparks.org/parks-and-trails/gamble-rogers-memorial-state-recreation-area-flagler-beach/hours-fees",
 caverns="https://www.floridastateparks.org/parks-and-trails/florida-caverns-state-park/experiences-amenities",
 cavernsh="https://www.floridastateparks.org/parks-and-trails/florida-caverns-state-park/hours-fees",
 littlet="https://www.floridastateparks.org/parks-and-trails/little-talbot-island-state-park/experiences-amenities",
 littleth="https://www.floridastateparks.org/parks-and-trails/little-talbot-island-state-park/hours-fees",
 kissimmee="https://www.floridastateparks.org/parks-and-trails/kissimmee-prairie-preserve-state-park/hours-fees",
 collier="https://www.floridastateparks.org/parks-and-trails/collier-seminole-state-park/experiences-amenities",
 collierh="https://www.floridastateparks.org/parks-and-trails/collier-seminole-state-park/hours-fees",
 manatee="https://www.floridastateparks.org/parks-and-trails/manatee-springs-state-park/experiences-amenities",
 manateehome="https://www.floridastateparks.org/parks-and-trails/manatee-springs-state-park")
def src(*k): return ' <span class="src">['+', '.join(f'<a href="{S.get(x,x)}" rel="noopener">source</a>' for x in k)+']</span>'
REG={"panhandle":("Panhandle","Escambia Santa_Rosa Okaloosa Walton Holmes Washington Bay Jackson Calhoun Gulf Franklin Liberty Gadsden Leon Wakulla Jefferson"),
"north":("North Florida","Madison Taylor Hamilton Suwannee Lafayette Dixie Columbia Gilchrist Levy Alachua Union Bradford Baker Nassau Duval Clay St._Johns Putnam Flagler Marion"),
"central":("Central Florida","Volusia Lake Sumter Citrus Hernando Seminole Orange Osceola Brevard Polk Indian_River Okeechobee Highlands"),
"tampa-bay-southwest":("Tampa Bay and Southwest","Pasco Pinellas Hillsborough Manatee Sarasota Hardee DeSoto Charlotte Lee Glades Hendry Collier"),
"southeast-keys":("Southeast and Keys","St._Lucie Martin Palm_Beach Broward Miami-Dade Monroe")}
C2R={c.replace("_"," "):k for k,(n,cs) in REG.items() for c in cs.split()}
def region(county): return C2R[county.replace(' County','').strip()]
# --- load data
off=json.load(open(os.path.join(HERE,'official.json')))
checked=json.load(open(os.path.join(HERE,'checked_no_dump.json')))
osm=json.load(open(os.path.join(HERE,'osm_enriched.json')))
GEO=json.load(open(os.path.join(HERE,'coordinates.json')))
PLACES=GEO['places']
STATE_PARKS=GEO['state_parks']
recs=[]
for o in off:
    g=PLACES[o['id']]
    o['directions_address']=g.get('directions_address')
    o['directions_source']=g.get('directions_source')
    o['coord_method']=g.get('method')
    if g.get('confident'):
        assert o.get('lat') is not None and abs(float(o['lat'])-float(g['lat']))<1e-6 and abs(float(o['lon'])-float(g['lon']))<1e-6, o['id']
    else:
        assert o.get('lat') is None and o.get('lon') is None, o['id']
    o['region']=region(o['county']); recs.append(o)
linked={4036349956}
for e in osm:
    if e['id'] in linked: continue
    t=e['tags']; r=e['_rev']; county=(r['county'] or '').replace(' County','')
    road=r.get('road'); place=r.get('city')
    nm=t.get('name') or ("Dump station"+(f" off {road}" if road else "")+(f", {place}" if place else ""))
    fee={'yes':'Yes (amount '+t['charge']+')' if 'charge' in t else 'Yes, amount not stated','no':'No (free)'}.get(t.get('fee'),'Not stated by source')
    acc={'customers':'Customers only (OSM tag)','yes':'Public (OSM tag)'}.get(t.get('access'),'Not stated by source')
    wat={'yes':'Yes (OSM tag)','no':'No (OSM tag)'}.get(t.get('water_point'),'Not stated by source')
    extra=[]
    if t.get('operator'): extra.append('Operator tag: '+t['operator'])
    if t.get('sanitary_dump_station:round_drain')=='yes': extra.append('Round drain (OSM tag)')
    dparts=[]
    if road:
        dparts.append(road)
        if place: dparts.append(place)
        if r.get('county'): dparts.append(r['county'])
        dparts.append('Florida')
        if r.get('postcode'): dparts.append(str(r['postcode']))
    recs.append(dict(id=f"osm-{e['id']}",name=nm,operator=t.get('operator','Not stated by source'),address=(road or 'Not stated by source'),city=place or 'Not stated by source',county=county,
      lat=e['lat'],lon=e['lon'],fee=fee,access=acc,water=wat,hours=t.get('opening_hours','Not stated by source'),notes='; '.join(extra),quote='',
      source=f"https://www.openstreetmap.org/node/{e['id']}",level="Community (OpenStreetMap)",region=region(county),
      directions_address=(', '.join(dparts) if dparts else None),directions_source=f"https://www.openstreetmap.org/node/{e['id']}",coord_method='osm-node'))
json.dump(recs,open(os.path.join(HERE,'stations_merged.json'),'w'),indent=1)
CSS=open(os.path.join(HERE,'style.css')).read()
NAV=open(os.path.join(HERE,'nav.js')).read()
MAPJS=open(os.path.join(HERE,'map.js')).read()
MONTHS={"January":"01","February":"02","March":"03","April":"04","May":"05","June":"06","July":"07","August":"08","September":"09","October":"10","November":"11","December":"12"}
WARNS=0
SM={}
_F="""
A 01110 10001 10001 11111 10001 10001 10001
B 11110 10001 10001 11110 10001 10001 11110
C 01110 10001 10000 10000 10000 10001 01110
D 11110 10001 10001 10001 10001 10001 11110
E 11111 10000 10000 11110 10000 10000 11111
F 11111 10000 10000 11110 10000 10000 10000
G 01110 10001 10000 10111 10001 10001 01110
H 10001 10001 10001 11111 10001 10001 10001
I 01110 00100 00100 00100 00100 00100 01110
J 00001 00001 00001 00001 10001 10001 01110
K 10001 10010 10100 11000 10100 10010 10001
L 10000 10000 10000 10000 10000 10000 11111
M 10001 11011 10101 10001 10001 10001 10001
N 10001 11001 10101 10011 10001 10001 10001
O 01110 10001 10001 10001 10001 10001 01110
P 11110 10001 10001 11110 10000 10000 10000
Q 01110 10001 10001 10001 10101 10010 01101
R 11110 10001 10001 11110 10100 10010 10001
S 01111 10000 10000 01110 00001 00001 11110
T 11111 00100 00100 00100 00100 00100 00100
U 10001 10001 10001 10001 10001 10001 01110
V 10001 10001 10001 10001 10001 01010 00100
W 10001 10001 10001 10101 10101 10101 01010
X 10001 10001 01010 00100 01010 10001 10001
Y 10001 10001 01010 00100 00100 00100 00100
Z 11111 00001 00010 00100 01000 10000 11111
"""
FONT={line.split()[0]:line.split()[1:] for line in _F.strip().splitlines()}
FONT[' ']=['00000']*7
FAVICON='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><title>Florida RV Dump Stations</title><rect width="32" height="32" rx="7" fill="#12352C"/><path fill="#ffffff" d="M16 5c-4.1 0-7.4 3.2-7.4 7.3 0 5.5 7.4 14.2 7.4 14.2s7.4-8.7 7.4-14.2C23.4 8.2 20.1 5 16 5zm0 10.2a2.9 2.9 0 1 1 0-5.8 2.9 2.9 0 0 1 0 5.8z"/></svg>\n'
def iso_date(s):
    d,mon,y=s.split()
    return y+'-'+MONTHS[mon]+'-'+f'{int(d):02d}'
def plain(s):
    t=re.sub(r'<[^>]+>','',s)
    return re.sub(r'\s+',' ',H.unescape(t)).strip()
def check_meta(path,title,desc):
    global WARNS
    if len(title)<50 or len(title)>60:
        WARNS+=1
        print(f"WARNING: title length {len(title)} is outside 50-60 for {path}: {title}", file=sys.stderr)
    if len(desc)<120 or len(desc)>160:
        WARNS+=1
        print(f"WARNING: description length {len(desc)} is outside 120-160 for {path}: {desc}", file=sys.stderr)
    if "Florida, Florida" in title or "Florida, Florida" in desc:
        WARNS+=1
        print(f"WARNING: doubled Florida in title or description for {path}: {title}", file=sys.stderr)
def canon_for(path):
    if path=='404.html': return BASE+'/404/'
    return BASE+'/'+path.replace('index.html','')
def ld(obj):
    return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False).replace('<','\\u003c')+'</script>'
def crumb_ld(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i,"name":name,"item":url} for i,(name,url) in enumerate(items,1)]}
def article_ld(title,desc,canon,when):
    iso=iso_date(when)
    pub={"@type":"Organization","name":"Florida RV Dump Stations","url":BASE+"/"}
    return {"@context":"https://schema.org","@type":"Article","headline":title,"description":desc,
            "datePublished":iso,"dateModified":iso,"mainEntityOfPage":{"@type":"WebPage","@id":canon},
            "author":pub,"publisher":{**pub,"logo":{"@type":"ImageObject","url":BASE+"/apple-touch-icon.png"}}}
def website_ld(desc):
    return {"@context":"https://schema.org","@type":"WebSite","name":"Florida RV Dump Stations","url":BASE+"/","description":desc}
def organization_ld():
    return {"@context":"https://schema.org","@type":"Organization","name":"Florida RV Dump Stations","url":BASE+"/","logo":BASE+"/apple-touch-icon.png"}
def faq_ld(pairs):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":plain(a)}} for q,a in pairs]}
def new_canvas(w,h,color):
    return bytearray(bytes(color)*(w*h))
def put(buf,w,h,x,y,color):
    if 0<=x<w and 0<=y<h:
        i=(y*w+x)*3; buf[i:i+3]=bytes(color)
def draw_text(buf,w,h,text,x,y,scale,color):
    for ch in text:
        for ry,row in enumerate(FONT[ch]):
            bits=int(row,2)
            for cx in range(5):
                if bits&(1<<(4-cx)):
                    for dy in range(scale):
                        for dx in range(scale):
                            put(buf,w,h,x+cx*scale+dx,y+ry*scale+dy,color)
        x+=(5+1)*scale
def text_width(text,scale):
    return (len(text)*(5+1)-1)*scale if text else 0
def draw_centered(buf,w,h,text,y,scale,color):
    draw_text(buf,w,h,text,(w-text_width(text,scale))//2,y,scale,color)
def draw_pin(buf,w,h,cx,cy,r,fill,hole):
    tip=cy+int(round(r*1.85)); r2=r*r; h2=int(r*0.40)**2
    for y in range(max(0,cy-r), min(h,tip+1)):
        for x in range(max(0,cx-r), min(w,cx+r+1)):
            dx,dy=x-cx,y-cy
            on=dx*dx+dy*dy<=r2
            if not on and cy<y<=tip and abs(dx)<=r*(1-(y-cy)/(tip-cy))*0.62: on=True
            if on: put(buf,w,h,x,y, hole if dx*dx+dy*dy<=h2 else fill)
def write_png(path,w,h,buf):
    stride=w*3; raw=bytearray()
    for y in range(h):
        raw.append(0); raw.extend(buf[y*stride:(y+1)*stride])
    def chunk(tag,data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')
    open(path,'wb').write(png)
def render_og():
    w,h=1200,630; teal=(0x12,0x35,0x2c); white=(255,255,255); mist=(0xf4,0xf0,0xe6)
    buf=new_canvas(w,h,teal)
    draw_pin(buf,w,h,600,190,90,white,teal)
    draw_centered(buf,w,h,"FLORIDA RV DUMP STATIONS",410,6,white)
    draw_centered(buf,w,h,"SOURCED LIST BY REGION",478,4,mist)
    return w,h,buf
def render_icon():
    w=h=180; teal=(0x12,0x35,0x2c); buf=new_canvas(w,h,teal)
    draw_pin(buf,w,h,90,72,50, (255,255,255), teal)
    return w,h,buf
def assets():
    os.makedirs(OUT,exist_ok=True)
    vend=os.path.join(OUT,'vendor','leaflet')
    if os.path.isdir(vend): shutil.rmtree(vend)
    shutil.copytree(os.path.join(HERE,'vendor','leaflet'), vend)
    open(os.path.join(OUT,'favicon.svg'),'w').write(FAVICON)
    w,h,buf=render_icon(); write_png(os.path.join(OUT,'apple-touch-icon.png'),w,h,buf)
    w,h,buf=render_og(); write_png(os.path.join(OUT,'og.png'),w,h,buf)
def png_size(path):
    d=open(path,'rb').read(24); assert d[:8]==b'\x89PNG\r\n\x1a\n'
    return struct.unpack('>II', d[16:24])
def verify_site():
    htmls=[]
    for dp,_,fs in os.walk(OUT):
        for f in fs:
            if f.endswith('.html'): htmls.append(os.path.relpath(os.path.join(dp,f),OUT))
    for rel in htmls:
        text=open(os.path.join(OUT,rel)).read()
        assert '\u2014' not in text and '\u2013' not in text, rel
        assert 'Florida, Florida' not in text, rel
        assert text.count(DISCLAIMER)>=2, rel
        assert 'href="/disclaimer/"' in text and 'href="/favicon.svg"' in text and 'href="/apple-touch-icon.png"' in text, rel
        assert 'property="og:image" content="'+BASE+'/og.png"' in text, rel
        assert 'property="og:image:width" content="1200"' in text and 'property="og:image:height" content="630"' in text, rel
        assert 'name="twitter:card" content="summary_large_image"' in text, rel
        blocks=[json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text)]
        types={b.get('@type') for b in blocks}
        bc=next(b for b in blocks if b['@type']=='BreadcrumbList')
        assert bc['itemListElement'][0]['item']==BASE+'/'
        assert bc['itemListElement'][-1]['item'].startswith(BASE+'/')
        if rel=='index.html':
            assert types=={'WebSite','Organization','Article','BreadcrumbList','FAQPage'}, types
        elif rel=='404.html':
            assert types=={'BreadcrumbList'}, types
            assert 'name="robots" content="noindex"' in text
        else:
            assert types=={'Article','BreadcrumbList'}, (rel, types)
        if rel!='404.html':
            shown=re.search(r'Last checked: ([0-9]{1,2} [A-Za-z]+ [0-9]{4})', text).group(1)
            iso=iso_date(shown)
            art=next(b for b in blocks if b['@type']=='Article')
            assert art['datePublished']==iso and art['dateModified']==iso, (rel, iso, art)
        if '"@type": "FAQPage"' in text or any(b['@type']=='FAQPage' for b in blocks):
            assert rel=='index.html'
            visible=plain(text)
            faq=next(b for b in blocks if b['@type']=='FAQPage')
            assert faq['mainEntity']
            for ent in faq['mainEntity']:
                assert ent['name'] in text
                assert ent['acceptedAnswer']['text'] in visible
        else:
            assert 'Short FAQ' not in text
        expect=canon_for(rel)
        assert 'rel="canonical" href="'+expect+'"' in text, (rel, expect)
        assert 'Independent guide. Not a government website.' in text, rel
        assert 'src="/_vercel/insights/script.js"' in text, rel
        assert "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif" in text, rel
        assert 'scroll-margin-top:var(--scroll-pad)' in text, rel
        assert 'id="read-next"' in text, rel
        assert 'id="q"' in text, rel
        if 'id="loc-map"' in text:
            assert 'scrollWheelZoom:false' in text, rel
            assert 'https://www.openstreetmap.org/copyright' in text, rel
            assert 'Get directions' in text, rel
            assert 'target="_blank" rel="noopener"' in text, rel
            assert 'role="region"' in text and 'aria-label="' in text, rel
            assert 'id="map-data"' in text, rel
            assert '/vendor/leaflet/leaflet.js' in text and 'sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH' in text, rel
            assert 'maps.googleapis' not in text and 'maps/embed' not in text and 'unpkg.com/leaflet' not in text, rel
            assert '.loc-map{position:relative;z-index:0' in text, rel
        else:
            assert 'leaflet' not in text.lower(), rel
        for href in re.findall(r'href="([^"]*)"', text):
            if href.startswith('http://') or href.startswith('https://') or href.startswith('mailto:') or href.startswith('#'): continue
            assert href.startswith('/') and 'index.html' not in href and not href.endswith('.html'), (rel, href)
        if VERIFY.get('google-site-verification'): assert VERIFY['google-site-verification'] in text
        else: assert 'google-site-verification' not in text
        if VERIFY.get('msvalidate.01'): assert VERIFY['msvalidate.01'] in text
        else: assert 'msvalidate.01' not in text
    sm=open(os.path.join(OUT,'sitemap.xml')).read()
    assert sm.count('<url>')==len(htmls)-1
    assert BASE+'/disclaimer/</loc>' in sm and '404' not in sm
    assert sm.count('<lastmod>')==len(htmls)-1
    for rel in htmls:
        if rel=='404.html': continue
        shown=re.search(r'Last checked: ([0-9]{1,2} [A-Za-z]+ [0-9]{4})', open(os.path.join(OUT,rel)).read()).group(1)
        loc=BASE+'/'+rel.replace('index.html','')
        assert f'<loc>{loc}</loc><lastmod>{iso_date(shown)}</lastmod>' in sm, (rel, shown)
    assert png_size(os.path.join(OUT,'og.png'))==(1200,630)
    assert png_size(os.path.join(OUT,'apple-touch-icon.png'))==(180,180)
    svg=open(os.path.join(OUT,'favicon.svg')).read()
    assert svg.strip().startswith('<svg') and '\u2014' not in svg and '\u2013' not in svg
    check_contrast()
    check_links()
def _lin(rgb):
    def f(c):
        c=c/255
        return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b=[f(c) for c in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def _contrast(a,b):
    hi,lo=max(_lin(a),_lin(b)),min(_lin(a),_lin(b))
    return (hi+0.05)/(lo+0.05)
def _hex(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))
def _srgb_lin(c):
    c=c/255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def _lin_srgb(c):
    v=12.92*c if c<=0.0031308 else 1.055*(max(c,0)**(1/2.4))-0.055
    return max(0,min(255,round(v*255)))
def _oklab(rgb):
    R,G,B=[_srgb_lin(c) for c in rgb]
    l=0.4122214708*R+0.5363325363*G+0.0514459929*B
    m=0.2119034982*R+0.6806995451*G+0.1073969566*B
    s=0.0883024619*R+0.2817188376*G+0.6299787005*B
    l_,m_,s_=l**(1/3),m**(1/3),s**(1/3)
    return (0.2104542553*l_+0.7936177850*m_-0.0040720468*s_,1.9779984951*l_-2.4285922050*m_+0.4505937099*s_,0.0259040371*l_+0.7827717662*m_-0.8086757660*s_)
def _oklab_rgb(Lab):
    L,a,b=Lab
    l_=L+0.3963377774*a+0.2158037573*b
    m_=L-0.1055613458*a-0.0638541728*b
    s_=L-0.0894841775*a-1.2914855480*b
    l,m,s=l_**3,m_**3,s_**3
    R=4.0767416621*l-3.3077115913*m+0.2309699292*s
    G=-1.2684380046*l+2.6097574011*m-0.3413193965*s
    B=-0.0041960863*l-0.7034186147*m+1.7076147010*s
    return tuple(_lin_srgb(c) for c in (R,G,B))
def check_contrast():
    white=(255,255,255)
    stops=[_hex(h) for h in ('12352C','3D2A1C','1A3330')]
    for i in range(len(stops)-1):
        for space in ('srgb','oklab'):
            for step in range(9):
                t=step/8
                if space=='srgb':
                    rgb=tuple(round(stops[i][k]*(1-t)+stops[i+1][k]*t) for k in range(3))
                else:
                    A,B=_oklab(stops[i]),_oklab(stops[i+1])
                    rgb=_oklab_rgb(tuple(A[k]*(1-t)+B[k]*t for k in range(3)))
                ratio=_contrast(white,rgb)
                if ratio<4.5:
                    raise SystemExit(f'Header gradient contrast {ratio:.2f} at {space} t={t:.2f}')
    for s in stops:
        mix=tuple(round(c+0.14*(255-c)) for c in s)
        if _contrast(white,mix)<4.5:
            raise SystemExit('Chip highlight contrast failed')
        if _contrast(_hex('F0D48A'),s)<3:
            raise SystemExit('Gold indicator contrast failed')
    pairs=[('#1C1915','#F4F0E6',4.5),('#1C1915','#ffffff',4.5),('#083656','#F4F0E6',4.5),('#083656','#ffffff',4.5),
           ('#4C2A6E','#F4F0E6',4.5),('#4C2A6E','#ffffff',4.5),('#1A140C','#F3D48A',4.5),('#1C1915','#fff8ec',4.5),
           ('#1C1915','#eef4f1',4.5),('#1C1915','#dff3e4',4.5),('#1C1915','#fdebd3',4.5),('#1C1915','#e7efe9',4.5),
           ('#143024','#e5f2ea',4.5),('#3e3a34','#F4F0E6',4.5),('#3e3a34','#ffffff',4.5),('#ffffff','#14241C',4.5)]
    for fg,bg,minimum in pairs:
        ratio=_contrast(_hex(fg),_hex(bg))
        if ratio<minimum:
            raise SystemExit(f'Contrast {ratio:.2f} below {minimum} for {fg} on {bg}')
def check_links():
    htmls={}
    for dp,_,fs in os.walk(OUT):
        for f in fs:
            if f.endswith('.html'):
                rel=os.path.relpath(os.path.join(dp,f),OUT)
                htmls[rel]=open(os.path.join(OUT,rel),encoding='utf-8').read()
    missing=[]
    def idset(text):
        return set(re.findall(r'\bid="([^"]*)"', text))
    for rel,text in htmls.items():
        found=re.findall(r'\bid="([^"]*)"', text)
        if len(found)!=len(set(found)):
            missing.append(rel+' duplicate ids '+', '.join(sorted({i for i in found if found.count(i)>1})))
        ids=set(found)
        for href_v in re.findall(r'\bhref="([^"]*)"', text):
            if href_v.startswith(('http://','https://','mailto:','tel:')): continue
            url,_,frag=href_v.partition('#')
            if url=='':
                if frag and frag not in ids: missing.append(f'{rel} -> {href_v}')
                continue
            if not url.startswith('/'):
                missing.append(f'{rel} bad {href_v}'); continue
            path=url.lstrip('/')
            target='index.html' if path=='' else (path+'index.html' if path.endswith('/') else path)
            dest_text=htmls.get(target)
            if dest_text is None:
                fp=os.path.join(OUT, target if not path.endswith('/') else path[:-1])
                alt=os.path.join(OUT, path if not path.endswith('/') else target)
                if os.path.isfile(os.path.join(OUT, path)) or os.path.isfile(os.path.join(OUT, target)):
                    if frag:
                        raw=open(os.path.join(OUT, target),encoding='utf-8').read() if os.path.isfile(os.path.join(OUT, target)) else ''
                        if frag and frag not in idset(raw): missing.append(f'{rel} -> {href_v}')
                    continue
                missing.append(f'{rel} -> {href_v}'); continue
            if frag and frag not in idset(dest_text):
                missing.append(f'{rel} -> {href_v}')
    if missing:
        raise SystemExit('Link check failed:\n'+'\n'.join(missing))
def slug(t):
    t=H.unescape(re.sub(r'<[^>]+>','',t))
    return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
def page_href(path):
    if path in ('index.html','/'): return '/'
    if path=='404.html': return '/404/'
    if path.endswith('/index.html'): return '/'+path[:-len('index.html')]
    return '/'+path
GROUPS=[
 ("Find a station",[
  ("regions/panhandle/index.html","Panhandle"),
  ("regions/north/index.html","North Florida"),
  ("regions/central/index.html","Central Florida"),
  ("regions/tampa-bay-southwest/index.html","Tampa Bay and Southwest"),
  ("regions/southeast-keys/index.html","Southeast and Keys")]),
 ("Fees and rules",[
  ("fees/index.html","Fees and access"),
  ("state-parks/index.html","State park dumps"),
  ("rules/index.html","Dumping rules")]),
 ("About this guide",[
  ("disclaimer/index.html","Disclaimer"),
  ("find/index.html","All pages")])]
GROUP_OF={p:g for g,items in GROUPS for p,_t in items}
TITLES={p:t for g,items in GROUPS for p,t in items}
TITLES['index.html']='Home'
TITLES['404.html']='Page not found'
ORDER=["regions/panhandle/index.html","regions/north/index.html","regions/central/index.html","regions/tampa-bay-southwest/index.html","regions/southeast-keys/index.html"]
READ_NEXT={
 "index.html":["state-parks/index.html","fees/index.html","rules/index.html"],
 "regions/panhandle/index.html":["regions/north/index.html","fees/index.html","rules/index.html"],
 "regions/north/index.html":["regions/central/index.html","fees/index.html","rules/index.html"],
 "regions/central/index.html":["regions/tampa-bay-southwest/index.html","fees/index.html","rules/index.html"],
 "regions/tampa-bay-southwest/index.html":["regions/southeast-keys/index.html","fees/index.html","rules/index.html"],
 "regions/southeast-keys/index.html":["fees/index.html","rules/index.html","regions/panhandle/index.html"],
 "fees/index.html":["state-parks/index.html","rules/index.html","disclaimer/index.html"],
 "state-parks/index.html":["fees/index.html","rules/index.html","index.html"],
 "rules/index.html":["state-parks/index.html","fees/index.html","index.html"],
 "disclaimer/index.html":["rules/index.html","fees/index.html","find/index.html"],
 "find/index.html":["index.html","fees/index.html","rules/index.html"],
 "404.html":["index.html","find/index.html","rules/index.html"]}
SUMMARIES={}
KW={}
VOID_TAGS={'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'}
def split_at_first_h2(body):
    depth=0
    for m in re.finditer(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', body):
        name=m.group(2).lower(); closing=m.group(1)=='/'; attrs=m.group(3) or ''
        if name=='h2' and not closing and depth==0:
            return body[:m.start()], body[m.start():]
        if closing: depth=max(0, depth-1)
        elif name not in VOID_TAGS and not attrs.rstrip().endswith('/'): depth+=1
    return body,''
def search_json():
    rows=[{"u":"/","t":"Home","s":SUMMARIES.get("index.html",""),"g":"Home","k":KW.get("index.html","")}]
    for g,items in GROUPS:
        for p,t in items:
            rows.append({"u":page_href(p),"t":t,"s":SUMMARIES.get(p,""),"g":g,"k":KW.get(p,"")})
    return json.dumps(rows,ensure_ascii=False).replace("<","\\u003c")
def topic_nav(path):
    bits=[]
    for g,items in GROUPS:
        links=[]; here=False
        for p,t in items:
            cur=' aria-current="page"' if p==path else ''
            cls=' class="is-current"' if p==path else ''
            if p==path: here=True
            links.append(f'<a href="{page_href(p)}"{cls}{cur}>{H.escape(t)}</a>')
        mark=' aria-current="true"' if here else ''
        bits.append(f'<details class="grp{" has-current" if here else ""}"><summary{mark}>{H.escape(g)}</summary><div class="glinks">'+''.join(links)+'</div></details>')
    return ''.join(bits)
def visible_crumbs(path):
    if path=='index.html':
        return '<nav class="crumbs" aria-label="Breadcrumb"><ol><li><span aria-current="page">Home</span></li></ol></nav>'
    items=['<li><a href="/">Home</a></li>']
    g=GROUP_OF.get(path)
    if g: items.append(f'<li><a href="/#{slug(g)}">{H.escape(g)}</a></li>')
    items.append(f'<li><span aria-current="page">{H.escape(TITLES.get(path,path))}</span></li>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>'+''.join(items)+'</ol></nav>'
def crumb_items(path):
    items=[("Home", BASE+"/")]
    if path!='index.html':
        g=GROUP_OF.get(path)
        if g: items.append((g, BASE+"/#"+slug(g)))
        url=BASE+"/404/" if path=='404.html' else canon_for(path)
        items.append((TITLES.get(path,path), url))
    return items
MARK='<svg class="mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path fill="#ffffff" d="M16 5c-4.1 0-7.4 3.2-7.4 7.3 0 5.5 7.4 14.2 7.4 14.2s7.4-8.7 7.4-14.2C23.4 8.2 20.1 5 16 5zm0 10.2a2.9 2.9 0 1 1 0-5.8 2.9 2.9 0 0 1 0 5.8z"/></svg>'
SEARCH_ICON='<svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
def page(path,title,body,desc,checked=None,crumbs=None,article=True,faq=None,robots=None,sitemap=None):
    when=checked or D
    check_meta(path,title,desc)
    canon=canon_for(path); SM[path]=sitemap or iso_date(when)
    summary=SUMMARIES.get(path,'')
    if '<h1>' in body:
        body=body.replace('<h1>','<h1 id="page-title">',1)
    if summary and path!='404.html' and '</h1>' in body:
        body=body.replace('</h1>','</h1><div class="inshort"><p><strong>In short.</strong> '+H.escape(summary)+'</p></div>',1)
    body=re.sub(r'<h2>(.*?)</h2>', lambda m: f'<h2 id="{slug(m.group(1))}">{m.group(1)}</h2>', body)
    h2s=re.findall(r'<h2 id="([^"]*)">(.*?)</h2>', body)
    toc=''
    if len(h2s)>=2:
        lis=''.join(f'<li><a href="#{i}">{H.escape(H.unescape(re.sub(r"<[^>]+>","",inner)))}</a></li>' for i,inner in h2s)
        toc=f'<nav class="toc" aria-label="On this page"><details class="toc-details" open><summary>On this page</summary><ul>{lis}</ul></details></nav>'
    def step_link(target, kind):
        label=TITLES.get(target)
        if not label: return ''
        word='Previous' if kind=='prev' else 'Next'
        return f'<a class="{kind}" href="{page_href(target)}"><span class="pn-k">{word}</span><span class="pn-t">{H.escape(label)}</span></a>'
    pn=''
    if path in ORDER:
        i=ORDER.index(path)
        prev=step_link(ORDER[i-1],'prev') if i else ''
        nxt=step_link(ORDER[i+1],'next') if i+1<len(ORDER) else ''
        if prev or nxt:
            pn='<nav class="pn" aria-label="Regions in order">'+prev+nxt+'</nav>'
    rn=[]
    for dest in READ_NEXT.get(path) or []:
        label=TITLES.get(dest)
        if not label: continue
        blurb=SUMMARIES.get(dest,'')
        blurb_html=f'<span class="ls">{H.escape(blurb)}</span>' if blurb else ''
        rn.append(f'<li><a class="jump" href="{page_href(dest)}"><span class="lt">{H.escape(label)}</span>{blurb_html}</a></li>')
    readnext='<aside class="readnext" aria-labelledby="read-next"><h2 id="read-next">Read next</h2><ul>'+''.join(rn)+'</ul></aside>' if rn else ''
    head_html, rest = split_at_first_h2(body)
    tail=pn+readnext
    rest=(rest+tail) if rest else tail
    if toc:
        layout=f'<div class="layout has-toc">{toc}<div class="rest">{rest}</div></div>'
    elif rest:
        layout=f'<div class="layout"><div class="rest">{rest}</div></div>'
    else:
        layout=''
    blocks=[]
    if path=='index.html':
        blocks.append(website_ld(desc)); blocks.append(organization_ld())
    if article: blocks.append(article_ld(title,desc,canon,when))
    blocks.append(crumb_ld(crumb_items(path)))
    if faq: blocks.append(faq_ld(faq))
    og='article' if article and path not in ('index.html','404.html') else 'website'
    img=BASE+'/og.png'; e=H.escape
    head=['<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
          '<meta name="theme-color" content="#12352C">',
          '<title>'+e(title)+'</title>','<meta name="description" content="'+e(desc)+'">','<link rel="canonical" href="'+e(canon)+'">',
          '<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
          '<meta property="og:type" content="'+og+'"><meta property="og:site_name" content="Florida RV Dump Stations"><meta property="og:locale" content="en_US">',
          '<meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(desc)+'"><meta property="og:url" content="'+e(canon)+'">',
          '<meta property="og:image" content="'+img+'"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Florida RV Dump Stations">',
          '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(desc)+'"><meta name="twitter:image" content="'+img+'"><meta name="twitter:image:alt" content="Florida RV Dump Stations">']
    for name,val in VERIFY.items():
        if val: head.append('<meta name="'+e(name)+'" content="'+e(val)+'" />')
    if robots: head.append('<meta name="robots" content="'+e(robots)+'">')
    head.extend(ld(b) for b in blocks)
    head.append('<style>'+CSS+'</style><script defer src="/_vercel/insights/script.js"></script></head>')
    brand_cur=' aria-current="page"' if path=='index.html' else ''
    header=(f'<div id="head-slot"><header id="site-header"><div class="shell">'
        f'<div class="brand-block"><a class="brand" href="/"{brand_cur}>{MARK}<span class="name-main">Florida RV Dump Stations</span><span class="name-compact">Dump stations</span></a>'
        f'<p class="name-sub">Independent guide. Not a government website.</p></div>'
        f'<button type="button" class="search-toggle" aria-expanded="false" aria-controls="site-search">{SEARCH_ICON}<span class="search-toggle-text">Search</span></button>'
        f'<div class="search-wrap" id="site-search"><form class="sitesearch" role="search" action="/find/" method="get">'
        f'<label for="q">Search this guide</label><input id="q" name="q" type="search" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false">'
        f'<button type="submit">Search</button></form>'
        f'<div id="search-results" class="search-results" hidden role="region" aria-live="polite" aria-label="Matching pages"></div></div>'
        f'<nav id="site-nav" class="top" aria-label="Topics">{topic_nav(path)}</nav>'
        f'<span class="nav-fade nav-fade-left" aria-hidden="true"></span><span class="nav-fade nav-fade-right" aria-hidden="true"></span><span class="nav-hint" aria-hidden="true"></span>'
        f'</div></header></div>')
    def foot_a(href, text):
        cur=' aria-current="page"' if page_href(path)==href else ''
        return f'<a href="{href}"{cur}>{text}</a>'
    foot=(f'<footer><div class="shell"><nav class="footnav" aria-label="About this guide">{foot_a("/","Home")}{foot_a("/fees/","Fees and access")}{foot_a("/state-parks/","State park dumps")}{foot_a("/rules/","Dumping rules")}{foot_a("/find/","All pages")}{foot_a("/disclaimer/","Disclaimer")}</nav>'
          f'<p class="disclaimer">{e(DISCLAIMER)}</p><p>Independent, unofficial guide. Not affiliated with Florida State Parks, FDOT, the Florida Department of Health, the Florida Department of Environmental Protection, Love\'s or OpenStreetMap. Official listings are linked to the operator page they came from. Community listings come from OpenStreetMap contributors (data &copy; OpenStreetMap contributors, ODbL)'
          +src('osmc')+f'. Dump stations close, change rules and charge new fees without notice: always call ahead. Last checked: {e(when)}.</p></div></footer>')
    article_html=f'<article class="content" aria-labelledby="page-title"><div class="head-block">{head_html}</div>{layout}</article>'
    main=(f'<main id="content" tabindex="-1"><div class="shell">{visible_crumbs(path)}'
          f'<p class="meta"><span class="checked">Last checked: {e(when)}</span></p>'
          f'<p class="disclaimer">{e(DISCLAIMER)}</p>{article_html}</div></main>')
    extra_script=('<script>'+MAPJS+'</script>') if 'id="loc-map"' in body else ''
    scripts=f'<script type="application/json" id="search-data">{search_json()}</script><script>{NAV}</script>'+extra_script
    h=''.join(head)+'<body><a class="skip" href="#content">Skip to content</a>'+header+main+foot+scripts+'</body></html>'
    assert '\u2014' not in h and '\u2013' not in h, path
    p=os.path.join(OUT,path); os.makedirs(os.path.dirname(p) or OUT, exist_ok=True); open(p,'w').write(h)
CALL='<div class="card note"><strong>Call ahead.</strong> Hours, fees, gate codes and who may use a station change often, and many park stations are for registered campers only. Confirm with the operator before you drive there.</div>'
def directions_href(address):
    return 'https://www.google.com/maps/dir/?api=1&destination='+urllib.parse.quote(address, safe='')
def directions_link(address, name):
    if not address: return ''
    href=H.escape(directions_href(address))
    return f'<a class="dirs" href="{href}" target="_blank" rel="noopener">Get directions<span class="sr"> to {H.escape(name)} (opens in a new tab)</span></a>'
def address_line(row):
    addr=row.get('directions_address'); src=row.get('directions_source')
    if not addr or not src: return ''
    street=addr.split(',')[0]
    if street and street in (row.get('address') or ''): return ''
    return f'<br><span class="src">{H.escape(addr)} [<a href="{H.escape(src)}" rel="noopener">source</a>]</span>'
def where_text(row):
    bits=[]
    city=row.get('city') or ''
    if city and not city.startswith('Not stated'): bits.append(city)
    county=row.get('county') or ''
    if county and not county.startswith('Not stated'): bits.append(county+' County')
    return ', '.join(bits)
def map_points(rows, href_for):
    pts=[]
    for x in rows:
        if x.get('lat') is None or x.get('lon') is None: continue
        pts.append({"id":x["id"],"name":x["name"],"lat":float(x["lat"]),"lon":float(x["lon"]),
            "where":where_text(x),"directions":(directions_href(x["directions_address"]) if x.get("directions_address") else None),
            "href":href_for(x)})
    return pts
def map_html(points, heading, label, note):
    if not points: return f'<h2>{H.escape(heading)}</h2><p class="map-note">{H.escape(note)}</p>'
    payload=json.dumps(points, ensure_ascii=False).replace('<','\\u003c')
    return (f'<h2>{H.escape(heading)}</h2><p class="map-note">{H.escape(note)}</p>'
        f'<div id="loc-map" class="loc-map" role="region" aria-label="{H.escape(label)}" data-label="{H.escape(label)}">'
        f'<p class="map-fallback">The list on this page is the full set of locations. The map loads here when this part of the page is on screen.</p></div>'
        f'<script type="application/json" id="map-data">{payload}</script>')
MAP_REPORT=[]
def station_map(rows, place_name):
    pts=map_points(rows, lambda x:'#loc-'+str(x['id']))
    missing=len(rows)-len(pts)
    note=(f"The table is the full list of {len(rows)} stations. The map is an extra view. "
          f"It shows {len(pts)} stations. A community station is pinned at its OpenStreetMap point. "
          f"An official station is pinned at coordinates the operator publishes, or at a confident match of the operator street address in OpenStreetMap Nominatim. "
          f"A street-address pin is the matched address, not a surveyed dump inlet.")
    if missing:
        note+=f" {missing} {'station is' if missing==1 else 'stations are'} not on the map because a pin could not be placed with confidence."
    label=f"Map of {len(pts)} RV dump stations in {place_name}. The table is the full list. Base map from OpenStreetMap."
    MAP_REPORT.append((place_name,len(rows),len(pts)))
    return map_html(pts,"Map of stations on this page",label,note)
def park_dirs(key, repeat_address=True):
    item=next(x for x in STATE_PARKS if x['id']==key)
    g=PLACES[item['place']]
    link=directions_link(g.get('directions_address'), item['name'])
    if not link: return ''
    if not repeat_address: return ' '+link
    return ' '+link+f'<br><span class="src">{H.escape(g["directions_address"])} [<a href="{H.escape(g["directions_source"])}" rel="noopener">park page</a>]</span>'
def table(rows):
    t=('<div class="filter"><label for="station-filter">Filter by name, city or county</label>'
       '<input id="station-filter" type="search" placeholder="Filter by name, city or county" autocomplete="off" '
       'oninput="var v=this.value.toLowerCase();document.querySelectorAll(\'#station-table tr\').forEach(function(r){if(r.querySelector(\'td\'))r.style.display=r.textContent.toLowerCase().indexOf(v)>-1?\'\':\'none\'})">'
       '</div><div class="wrap"><table id="station-table"><tr><th scope="col">Station</th><th scope="col">Address / city</th><th scope="col">Coordinates</th><th scope="col">Fee</th><th scope="col">Who can use it</th><th scope="col">Potable water</th><th scope="col">Hours / season</th><th scope="col">Verification</th></tr>')
    for x in sorted(rows,key=lambda x:(x['level'].startswith('Community'),x['county'],x['name'])):
        co=f'<a href="https://www.openstreetmap.org/?mlat={x["lat"]}&amp;mlon={x["lon"]}#map=17/{x["lat"]}/{x["lon"]}" rel="noopener">{x["lat"]:.5f}, {x["lon"]:.5f}</a>' if x['lat'] else 'Not stated by source'
        s=f'<a href="{x["source"]}" rel="noopener">source</a>'+(f', <a href="{x["source2"]}" rel="noopener">OSM</a>' if x.get('source2') else '')
        q=f'<br><span class="src">Source says: "{H.escape(x["quote"])}"</span>' if x['quote'] else ''
        n=f'<br><span class="src">{H.escape(x["notes"])}</span>' if x['notes'] else ''
        lv='ok' if x['level'].startswith('Official') else 'comm'
        dlink=directions_link(x.get('directions_address'), x['name'])
        dhtml=(' '+dlink) if dlink else ''
        t+=f'<tr id="loc-{H.escape(str(x["id"]))}"><td><strong>{H.escape(x["name"])}</strong>{dhtml}{address_line(x)}{q}{n}</td><td>{H.escape(x["address"])}<br>{H.escape(x["city"])}, {H.escape(x["county"])} County</td><td>{co}</td><td>{H.escape(x["fee"])}</td><td>{H.escape(x["access"])}</td><td>{H.escape(x["water"])}</td><td>{H.escape(x["hours"])}</td><td><span class="lv {lv}">{x["level"]}</span> <span class="src">[{s}]</span></td></tr>'
    return t+'</table></div>'
LEVELS=f'''<div class="card"><strong>Verification levels</strong><ul><li><span class="lv ok">Official</span> the operator's own page (Florida State Parks, Love's) states a dump station, quoted in the table.</li>
<li><span class="lv ok">Official + OSM</span> official page plus an OpenStreetMap point that names the same operator, used only for coordinates and extra tags.</li>
<li><span class="lv comm">Community (OpenStreetMap)</span> mapped by volunteers as amenity=sanitary_dump_station{src('osm')}. Name, fee and access tags are often missing. Treat as a lead, not a confirmation.</li></ul></div>'''
cnt={k:sum(1 for x in recs if x['region']==k) for k in REG}
noff=sum(1 for x in recs if x['level'].startswith('Official')); ncom=len(recs)-noff
faq=[("Can I dump at a Florida interstate rest area?",f"Not according to any FDOT page we checked. The FDOT rest area page and facility list do not mention dump stations, and FDOT says overnight camping is not permitted and visitors may stay up to three hours{src('fdot','fdotlist')}. Some third-party apps list rest area dumps; we could not confirm those on an official source. The statute, the health rule, and the FDOT rest-area rule are on the <a href=\"/rules/\">dumping rules</a> page."),
("Can I use a state park dump station if I am not camping there?",f"Some park pages say, and some do not. The Florida State Parks fee schedule lists a dump station fee of $10 per unit for a non-registered camper, and it says to confirm the activity is available at that park{src('fspfee','fspfee2')}. Blue Spring says the fee is $10.65 if you are not a registered camper{src('bluespring')}. Fort Clinch says the stations are free for registered campers and available to day visitors for a fee, and it does not state the amount{src('fortclinch')}. The Manatee Springs home page says the dump station is currently closed, and its amenities page still says a dump station is provided{src('manateehome','manatee')}. The other park pages that state a rule are quoted on the <a href=\"/state-parks/\">state park dump</a> page."),
("Do I need a gate code?",f"At some parks, yes. Rainbow Springs says its campground gates are closed at all times and the code is given on your day of arrival{src('rainbow')}."),
("Are OpenStreetMap entries reliable?",f"They are community data{src('osm')}. Many Florida entries have no name, fee or access tags. We show them so you know where to look, flagged as Community, and they need a phone call to confirm."),
("Is there potable water at the dump?","Rarely stated by official sources. Where an OSM contributor tagged water_point we show it as an OSM tag. Never use the rinse hose for drinking water."),
("How current is this?",f"Station rows on this page were collected on {D}. The state park dump page was checked on {SP}. Each row links to its source so you can recheck.")]
SUMMARIES['index.html']=f'{len(recs)} stations on {D}: {noff} confirmed on an official page, {ncom} community-mapped. Confirm with the operator before you drive there.'
SUMMARIES['fees/index.html']='Most sources do not publish a dump fee. Below are the only fee statements we found, then a summary of access rules.'
SUMMARIES['state-parks/index.html']='The fee schedule says $10 per unit for a non-registered camper. Blue Spring says $10.65. Manatee Springs says its dump station is closed. Other park pages quoted here state who may use the station.'
SUMMARIES['rules/index.html']='Florida law limits where a recreational vehicle may empty black water, grey water, or any other liquid waste. This is an unofficial reading of the public texts, not legal advice.'
SUMMARIES['disclaimer/index.html']='Station names, locations, fees, access, hours and legal quotations on this site are taken from the linked public sources. Always confirm with the official source or the facility before you act.'
SUMMARIES['find/index.html']='Every page on this guide, grouped by topic. Use the search box to narrow the list.'
for k,(n,_cs) in REG.items():
    place={'Panhandle':'the Panhandle','Southeast and Keys':'the Southeast and the Keys'}.get(n,n)
    SUMMARIES[f'regions/{k}/index.html']=f'{cnt[k]} stations in {place}. Each row links to its source. Call ahead.'
    rows=[x for x in recs if x['region']==k]
    KW[f'regions/{k}/index.html']=' '.join(x['name']+' '+x['city']+' '+x['county']+' '+x.get('operator','') for x in rows)
KW['index.html']=' '.join(c['name'] for c in checked)+' etiquette rest area openstreetmap verification call ahead'
KW['rules/index.html']='rest area welcome center litter law statute grey water black water wastewater sanitary dump station health department transportation'
KW['fees/index.html']='fee access campers loves love state park customers potable water'
KW['state-parks/index.html']='state park campers day visitor non-registered fee hours closure koreshan oscar scherer blue spring fort clinch anastasia gamble rogers florida caverns little talbot kissimmee prairie collier seminole manatee springs'
KW['disclaimer/index.html']='liability warranty affiliation accuracy corrections'
KW['find/index.html']='index search all pages topics'
def jump(path, label=None):
    label=label or TITLES[path]
    blurb=SUMMARIES.get(path,'')
    extra=f'<span class="ls">{H.escape(blurb)}</span>' if blurb else ''
    return f'<a class="jump" href="{page_href(path)}"><span class="lt">{H.escape(label)}</span>{extra}</a>'
region_items=''.join(f'<li><a href="/regions/{k}/">{n}</a> ({cnt[k]} stations)</li>' for k,(n,_) in REG.items())
topics_html=''
for g,items in GROUPS:
    lis=''.join(f'<li>{jump(p)}</li>' for p,_t in items)
    topics_html+=f'<h3 id="topic-{slug(g)}">{H.escape(g)}</h3><ul class="link-grid">{lis}</ul>'
GUIDE=f'''<h2>Start here</h2>
<p>These groups follow a trip. Open the one that matches what you need to do.</p>
<ol class="timeline">
<li class="period"><h3 id="{slug("Find a station")}">Find a station</h3>
<h2>Pick a region</h2><ul class="grid">{region_items}</ul></li>
<li class="period"><h3 id="{slug("Fees and rules")}">Fees and rules</h3>
<p><a href="/fees/">Dump station fees and who can use them</a></p>
<p><a href="/state-parks/">Who may use a Florida State Park dump station</a></p>
<p><a href="/rules/">Where you can and cannot dump RV waste in Florida</a></p></li>
<li class="period"><h3 id="{slug("About this guide")}">About this guide</h3>
<ul class="link-grid"><li>{jump("disclaimer/index.html")}</li><li>{jump("find/index.html")}</li></ul></li>
</ol>
<h2>Top tasks</h2>
<p>The pages and sections people need most often.</p>
<ul class="tasks">
<li><a class="jump" href="#how-to-use-a-dump-station"><span class="lt">How to use a dump station</span><span class="ls">Six steps for emptying tanks at a station. Always follow posted signs at the station.</span></a></li>
<li><a class="jump" href="/fees/"><span class="lt">Dump station fees and who can use them</span><span class="ls">{H.escape(SUMMARIES["fees/index.html"])}</span></a></li>
<li><a class="jump" href="/state-parks/"><span class="lt">Who may use a Florida State Park dump station</span><span class="ls">{H.escape(SUMMARIES["state-parks/index.html"])}</span></a></li>
<li><a class="jump" href="/rules/"><span class="lt">Where you can and cannot dump RV waste in Florida</span><span class="ls">{H.escape(SUMMARIES["rules/index.html"])}</span></a></li>
<li><a class="jump" href="#etiquette"><span class="lt">Etiquette</span><span class="ls">Be quick when others are waiting. Never use the rinse hose to fill your fresh water tank.</span></a></li>
<li><a class="jump" href="#short-faq"><span class="lt">Short FAQ</span><span class="ls">Rest areas, day visitors, gate codes, OpenStreetMap, drinking water, and how current this list is.</span></a></li>
<li><a class="jump" href="#checked-no-dump-station-stated"><span class="lt">Checked, no dump station stated</span><span class="ls">Places checked where the source does not state a dump station.</span></a></li>
<li>{jump("disclaimer/index.html")}</li>
<li>{jump("find/index.html")}</li>
</ul>
<h2>All topics</h2>
<p>Every page on this guide, grouped by topic.</p>
{topics_html}'''
body=f'''<h1>Florida RV dump stations: sourced list by region</h1>
<p>A plain list of places in Florida where an RV can empty black and grey tanks, taken only from operator pages (Florida State Parks, Love's) and OpenStreetMap community data. {len(recs)} stations on {D}: {noff} confirmed on an official page, {ncom} community-mapped.</p>{CALL}
{GUIDE}
<h2>How to use a dump station</h2><div class="card"><ol><li>Pull up so your sewer outlet is on the drain side. Set the parking brake.</li><li>Wear disposable gloves. Connect the sewer hose to your outlet first, then put the other end fully into the drain inlet and secure it.</li><li>Open the black tank valve first and let it empty completely.</li><li>Close it, then open the grey tank valve. Grey water helps flush the hose.</li><li>Close the valves, rinse the hose with the non-potable rinse water if provided, and drain it into the inlet.</li><li>Disconnect at the RV end first, rinse the area, and close the drain lid.</li></ol>
<p class="src">General practice guidance, not from a single official source. Always follow posted signs at the station.</p></div>
<h2>Etiquette</h2><div class="card"><ul><li>Be quick when others are waiting. Do tank flushing and hose cleaning at your site if you can.</li><li>Never use the rinse hose to fill your fresh water tank.</li><li>Leave the pad cleaner than you found it.</li><li>Pay any posted fee and respect campers-only signs.</li><li>Do not dump grey or black water anywhere other than an approved inlet. It is a health hazard.</li></ul></div>
{LEVELS}
<h2>Checked, no dump station stated</h2><div class="card"><ul>'''+''.join(f'<li><strong>{H.escape(c["name"])}</strong>: {H.escape(c["note"])} <span class="src">[<a href="{c["source"]}" rel="noopener">source</a>]</span></li>' for c in checked)+'''</ul></div>
<h2>Short FAQ</h2>'''+''.join(f'<div class="card"><strong>{q}</strong><p>{a}</p></div>' for q,a in faq)
if os.path.exists(OUT): shutil.rmtree(OUT)
page('index.html',"All Florida RV dump stations by region, with sources",body,"Florida RV dump stations from Florida State Parks, Love's and OpenStreetMap, listed by region, with fees, access, verification level and links to each source.",crumbs=[("Home",BASE+"/")],faq=faq)
REGION_SEO={
"panhandle":("RV dump stations in the Florida Panhandle, sourced","Sourced RV dump stations in the Florida Panhandle, with fees, access, potable water, hours and links to operator pages or OpenStreetMap."),
"north":("Sourced RV dump stations in North Florida, with fees","Sourced RV dump stations in North Florida, with fees, access, potable water, hours and links to operator pages or OpenStreetMap."),
"central":("Sourced RV dump stations in Central Florida, with fees","Sourced RV dump stations in Central Florida, with fees, access, potable water, hours and links to operator pages or OpenStreetMap."),
"tampa-bay-southwest":("RV dump stations in Tampa Bay and Southwest, Florida","Sourced RV dump stations in Tampa Bay and Southwest Florida, with fees, access, potable water, hours and links to operator pages or OpenStreetMap."),
"southeast-keys":("RV dump stations in the Southeast and Keys, Florida","Sourced RV dump stations in the Southeast and the Keys, with fees, access, potable water, hours and links to operator pages or OpenStreetMap.")}
for k,(n,cs) in REG.items():
    rows=[x for x in recs if x['region']==k]
    b=f'<h1>RV dump stations: {n}</h1><p>{len(rows)} stations. Counties in this region: {", ".join(c.replace("_"," ") for c in cs.split())}.</p>{CALL}'+table(rows)+station_map(rows,n)+LEVELS+'<p><a href="/">All regions</a> | <a href="/fees/">Fees</a> | <a href="/state-parks/">State park dumps</a> | <a href="/rules/">Dumping rules</a></p>'
    rt,rd=REGION_SEO[k]
    page(f'regions/{k}/index.html',rt,b,rd,crumbs=[("Home",BASE+"/"),(n,BASE+f"/regions/{k}/")])
fr=[x for x in recs if x['fee']!='Not stated by source']
fee_pts=map_points(fr, lambda x:'#loc-'+str(x['id']))
fee_missing=len(fr)-len(fee_pts)
fee_note=(f"The table above lists the {len(fr)} stations whose source states a fee. The map is an extra view of that list. "
    f"It shows {len(fee_pts)} stations. A community station is pinned at its OpenStreetMap point. "
    f"An official station is pinned at coordinates the operator publishes, or at a confident match of the operator street address in OpenStreetMap Nominatim. "
    f"A street-address pin is the matched address, not a surveyed dump inlet.")
if fee_missing:
    fee_note+=f" {fee_missing} {'station is' if fee_missing==1 else 'stations are'} not on the map because a pin could not be placed with confidence."
fee_label=f"Map of {len(fee_pts)} RV dump stations whose source states a fee. The table is the full list. Base map from OpenStreetMap."
MAP_REPORT.append(("Fees",len(fr),len(fee_pts)))
fee_map=map_html(fee_pts,"Map of stations on this page",fee_label,fee_note)
fb=f'''<h1>Florida RV dump station fees and access</h1><p>Most sources do not publish a dump fee. Below are the only fee statements we found, then a summary of access rules.</p>{CALL}
<h2>Fees that a source states</h2><div class="wrap"><table><tr><th scope="col">Station</th><th scope="col">County</th><th scope="col">Fee</th><th scope="col">Who can use it</th><th scope="col">Verification</th></tr>'''+''.join(f'<tr id="loc-{H.escape(str(x["id"]))}"><td>{H.escape(x["name"])} {directions_link(x.get("directions_address"), x["name"])}</td><td>{x["county"]}</td><td>{H.escape(x["fee"])}</td><td>{H.escape(x["access"])}</td><td>{x["level"]} <span class="src">[<a href="{x["source"]}" rel="noopener">source</a>]</span></td></tr>' for x in fr)+f'''</table></div>
<p>{len(recs)-len(fr)} of {len(recs)} stations: fee not stated by source.</p>
{fee_map}
<h2>Access summary</h2><div class="card"><ul>
<li>Florida State Parks dump stations are described as campground amenities. Anastasia says free for park campers{src('anastasia')}. Where a park page states who may use the station, what a non-camper pays, or that a station is closed, the quotes are on the <a href="/state-parks/">state park dump</a> page (checked {SP}). Rainbow Springs says a day-use reservation program began on April 29, 2026, and that all visitors need a reservation to enter the park. That page does not say a day visitor may use the dump station{src('rainbow')}. State park camping reservations: 800-326-3521{src('fspres')}.</li>
<li>Love's lists RV Dump Service among amenities at the four Florida locations we checked; price not stated on the location page{src('loves')}.</li>
<li>FDOT rest areas: no dump stations stated{src('fdot')}.</li>
<li>OpenStreetMap access tags: {sum(1 for x in recs if x['access'].startswith('Customers'))} customers only, {sum(1 for x in recs if x['access'].startswith('Public'))} public, rest not stated{src('osm')}.</li></ul></div>
<p>For the statute and the Department of Health rule on where a tank may be emptied, see <a href="/rules/">where you can and cannot dump</a>. For who may use a state park station, see <a href="/state-parks/">state park dump stations</a>.</p>'''
page('fees/index.html',"Florida RV dump station fees and access, with sources",fb,"Which Florida RV dump stations state a fee, who may use them, and how access is described on operator pages and OpenStreetMap tags.",crumbs=[("Home",BASE+"/"),("Fees",BASE+"/fees/")])
sp_pts=[]
for item in STATE_PARKS:
    g=PLACES[item['place']]
    if not item.get('map_pin'): continue
    assert g.get('method')=='nominatim' and g.get('confident') and g.get('lat') is not None, item['id']
    sp_pts.append({"id":item['id'],"name":item['name'],"lat":float(g['lat']),"lon":float(g['lon']),
        "where":g['directions_address'],"directions":directions_href(g['directions_address']),"href":"#loc-park-"+item['id']})
sp_missing=len(STATE_PARKS)-len(sp_pts)
sp_note=(f"The text on this page names {len(STATE_PARKS)} parks. The map is an extra view. "
    f"It shows {len(sp_pts)} parks whose street address matched one place in OpenStreetMap Nominatim. "
    f"A pin is that matched address, not a surveyed dump inlet. "
    f"{sp_missing} parks stay in the text and are not pinned, because the address match was not confident. "
    f"Map tiles are from OpenStreetMap. The quoted rules on this page do not come from OpenStreetMap.")
sp_label=f"Map of {len(sp_pts)} Florida State Parks named on this page. The text is the full information. Base map from OpenStreetMap."
MAP_REPORT.append(("State park dumps",len(STATE_PARKS),len(sp_pts)))
state_park_map=map_html(sp_pts,"Map of parks on this page",sp_label,sp_note)
sp=f'''<h1>Who may use a Florida State Park dump station</h1>
<p>This page quotes Florida State Parks pages that say who may use a dump station, what a person who is not a registered camper pays, or that a station is closed. It is not a list of every state park dump station. A page that only says a station exists is not given a row. The quoted rules on this page do not use OpenStreetMap or any other community listing.</p>
{CALL}
<h2>What the fee schedule says</h2>
<div class="card">
<p>The Division of Recreation and Parks posts fee-schedule PDFs on floridastateparks.org. On {SP}, two files whose names include 2021_05_10 were read. One of those file names also includes 05.2022. Both contain this line: "Dump Station Per unit, non-registered campers $10.00". The two files are not the same in every section. The difference found is about an adoptive-family entrance pass, not the dump station. A third posted file, whose name includes 2013_10_01, contains the same dump-station line.{src('fspfee','fspfee2','fspfee2013')}</p>
<p>The schedule says fees are per day unless otherwise noted. The dump line says "Per unit". It does not define a unit beyond those words. The dump line is not marked with the double asterisk the schedule uses for "Includes all state and local taxes."</p>
<p>The schedule also says: "Please confirm the recreational activity in which you want to participate is available at the location and on the date you plan to visit. Prices and availability subject to change without notice. County surcharges may apply." It gives the statewide information line as (850) 245-2157. It does not say that every park has a dump station. It does not say a registered camper pays nothing. It does not say whether a park entrance fee is charged in addition to the $10.</p>
<p>The schedule says this authority comes from Chapter 258, Florida Statutes, and Rule 62D-2.014, Florida Administrative Code. Section 258.014(1)(a) says the Division of Recreation and Parks "shall have the power to charge reasonable fees, rentals, or charges for the use or operation of facilities and concessions in state parks." That section does not name a dump station and does not set a dollar amount.{src('s258014')}</p>
</div>
<h2>Where official pages do not match</h2>
<div class="card">
<p>Blue Spring State Park says: "The fee is $10.65 to use the dump station if you are not a registered camper." The fee schedule says $10.00 per unit for non-registered campers. Both are Florida State Parks sources. They do not match. Neither page says that $10.65 is $10 plus tax, so this page does not treat it that way.{src('bluespring','fspfee')}</p>
<p>The Manatee Springs State Park home page says: "Effective Jan. 14, 2026: The Waterfront Restroom and dump station at Manatee Springs State Park are currently closed." The experiences and amenities page says: "There is no sewer hook-up in Magnolia 2 or Hickory but a dump station is provided." The home page does not say that another dump station remains open. The amenities page does not say the station is closed.{src('manateehome','manatee')}</p>
</div>
<h2>Parks that state who may use the station</h2>
<p>A row is included only when that park's own page states who may use the station or what a person who is not a registered camper pays. "Not stated" means that page does not say it. None of these hours pages states a separate opening time for the dump station. The hours below are the park hours on the hours page.</p>
<div class="wrap"><table>
<tr><th scope="col">Park</th><th scope="col">What the park page says</th><th scope="col">Fee on the park page</th><th scope="col">Park hours on the hours page</th></tr>
<tr id="loc-park-anastasia">
<td><a href="{S['anastasia']}" rel="noopener">Anastasia State Park</a>{park_dirs('anastasia')}</td>
<td>"A communal dump station is free for park campers." The page does not say whether a person who is not a park camper may use it.</td>
<td>Not stated on the park page.</td>
<td>Open from 8 a.m. until sundown, 365 days a year. The hours page does not mention the dump station. Campers arriving after sunset are told to call 904-461-2033 on the day of arrival. That instruction is for campers.</td>
</tr>
<tr id="loc-park-blue-spring">
<td><a href="{S['bluespring']}" rel="noopener">Blue Spring State Park</a>{park_dirs('blue-spring')}</td>
<td>"The dump station is located in the campground." The same page also says "A dump station is available in the park." It says: "The fee is $10.65 to use the dump station if you are not a registered camper." It also says: "A new day-use reservation program will be implemented at Blue Spring State Park beginning July 15, 2026. The window for advanced reservations opens July 8, 2026. All day-use visitors will be required to have a reservation to enter the park." It does not say that reservation is permission to use the dump station.</td>
<td>$10.65 if you are not a registered camper. The fee schedule says $10.00. See the section above. The hours page does not repeat the $10.65. It says the RV utility fee includes water and electricity, and it does not mention the dump station.</td>
<td>Open from 8 a.m. until sundown, 365 days a year.</td>
</tr>
<tr id="loc-park-collier">
<td><a href="{S['collier']}" rel="noopener">Collier-Seminole State Park</a>{park_dirs('collier')}</td>
<td>"A centralized dump station is available for RV campers." The page does not say whether a person who is not an RV camper may use it. The park home page uses the words "A dump station is available for RV campers."</td>
<td>Not stated. The hours page does not mention the dump station. It says the nightly utility fee includes water, electricity and sewer. That line does not say "dump station."</td>
<td>8 a.m. until sunset, 365 days a year. The park page gives the address as 20200 Tamiami Trail E. Naples FL 34114, and the amenities page gives the ranger station phone as (239) 393-7306.</td>
</tr>
<tr id="loc-park-caverns">
<td><a href="{S['caverns']}" rel="noopener">Florida Caverns State Park</a>{park_dirs('caverns')}</td>
<td>The equestrian section says three RV or trailer sites do not have sewer hookups, then: "Use of a communal dump station located at the entrance to the youth camp is free for park campers." The page does not say whether a day visitor may use it.</td>
<td>Not stated for a person who is not a park camper. The hours page says the nightly utility fee includes water, electricity and sewer. It does not mention the dump station.</td>
<td>The day-use portion is open daily, 8 a.m. until sunset CST.</td>
</tr>
<tr id="loc-park-fort-clinch">
<td><a href="{S['fortclinch']}" rel="noopener">Fort Clinch State Park</a>{park_dirs('fort-clinch')}</td>
<td>"Both campgrounds have a dump station." "The dump station facilities are free of charge to registered campers, and they are also available for day visitors for a fee."</td>
<td>The park page does not state the dollar amount. The hours page does not mention the dump station.</td>
<td>Open 8 a.m. to sunset daily.</td>
</tr>
<tr id="loc-park-gamble">
<td><a href="{S['gamble']}" rel="noopener">Gamble Rogers Memorial State Recreation Area, Flagler Beach</a>{park_dirs('gamble')}</td>
<td>"A communal dump station is free to park campers." The page does not say whether a person who is not a park camper may use it.</td>
<td>Not stated for a person who is not a park camper. The hours page does not mention the dump station. It says the nightly utility fee includes water, electricity and sewer. That line does not say "dump station."</td>
<td>Open 8 a.m. until sundown, 365 days a year.</td>
</tr>
<tr id="loc-park-kissimmee">
<td><a href="{S['kissimmee']}" rel="noopener">Kissimmee Prairie Preserve State Park</a>{park_dirs('kissimmee')}</td>
<td>The hours page ties dump use to the RV utility fee. It does not say that a day visitor may use the station, and it does not say that a tent camper may use it.</td>
<td>"$7 nightly utility fee for RV units. Utility fees include water, electricity and use of dump station. Utility fee does not apply to tent camping." A fee for a person who is not camping is not stated.</td>
<td>Open 8 a.m. until sundown, 365 days a year.</td>
</tr>
<tr id="loc-park-koreshan">
<td><a href="{S['koreshan']}" rel="noopener">Koreshan State Park</a>{park_dirs('koreshan')}</td>
<td>"$10 dump station use plus entrance fee for those not registered as campers."</td>
<td>$10, plus the entrance fee, for people who are not registered campers. Admission on the same page is $5 per vehicle (two to eight people), $4 for a single-occupant vehicle, and $2 for pedestrians, bicyclists, extra passengers, and passengers in a vehicle with the holder of an Annual Individual Entrance Pass. The fee schedule does not mention an entrance fee in the dump line.</td>
<td>Open 8 a.m. until sunset, 365 days a year. The camping office is open daily 9 a.m. until 5 p.m. The page does not say those office hours are the dump-station hours.</td>
</tr>
<tr id="loc-park-little-talbot">
<td><a href="{S['littlet']}" rel="noopener">Little Talbot Island State Park</a>{park_dirs('little-talbot')}</td>
<td>The camping section says: "A dump station is available at the campground exit for RV campers." The RV section on the same page says: "A dump station is available at the campground exit." It does not repeat "for RV campers." The page does not say whether a day visitor may use the station. The same page says the campground playground, the campground canoe and kayak launch, and the Campground Nature Trail are for registered campers only, with no day-visitor use. It does not put that sentence on the dump station.</td>
<td>Not stated. The hours page does not mention the dump station. It says the nightly utility fee includes water, electricity and sewer. That line does not say "dump station."</td>
<td>Open from 8 a.m. until sunset, 365 days a year.</td>
</tr>
<tr id="loc-park-oscar">
<td><a href="{S['oscar']}" rel="noopener">Oscar Scherer State Park</a>{park_dirs('oscar')}</td>
<td>"Dump station, non-registered campers $10. Does not include park entrance fee."</td>
<td>$10 for non-registered campers. The same page says that amount does not include the park entrance fee. Admission on that page is $5 per vehicle (up to eight people), $4 for a single-occupant vehicle, and $2 for pedestrians, bicyclists, extra passengers, and passengers in a vehicle with the card holder of an Annual Individual Entrance Pass. Sunset entrance is $4 per vehicle, for entry one hour prior to sunset. The dump bullet does not say the sunset rate applies to dumping.</td>
<td>Open 8 a.m. until sundown, 365 days a year.</td>
</tr>
</table></div>
<p>Hours pages: Anastasia, Blue Spring, Collier-Seminole, Florida Caverns, Fort Clinch, Gamble Rogers, Kissimmee Prairie, Koreshan, Little Talbot Island, and Oscar Scherer.{src('anastasiah','bluespringh','collierh','cavernsh','fortclinchh','gambleh','kissimmee','koreshan','littleth','oscar')}</p>
<p>The Collier-Seminole address is on the park page.{src('https://www.floridastateparks.org/parks-and-trails/collier-seminole-state-park')}</p>
<h2>A station the park page says is closed</h2>
<div class="card">
<p id="loc-park-manatee">Manatee Springs State Park, 11650 N.W. 115 St. Chiefland FL 32626. {park_dirs('manatee', False)} Phone 352-493-6072. The park page lists the hours as 8 a.m. to sunset, 365 days a year.{src('manateehome')}</p>
<p>That page says the waterfront restroom and dump station are currently closed, effective Jan. 14, 2026. The amenities page still says a dump station is provided for the Magnolia 2 and Hickory loops, which have no sewer hookup, and it does not say who may use it. Read both pages before you drive there. The two statements are also in the section above.{src('manateehome','manatee')}</p>
</div>
{state_park_map}
<h2>What these pages do not say</h2>
<div class="card">
<ul>
<li>No hours page in the table states a separate opening time for the dump station.</li>
<li>The fee schedule does not say registered campers pay nothing. "Free" is included above only where a park page says free.</li>
<li>The camping page says: "Full-facility campsites for tent campers and RVers include water, electricity, a grill and picnic table, along with centralized showers, restrooms and dump station." It does not name the parks. It does not state a fee, and it does not say a day visitor may use the station. It gives the reservation phone as 800-326-3521 or TDD 888-433-0287.{src('fspcamp')}</li>
<li>The Florida State Parks FAQ says: "Most parks have a central dump station." It does not name the parks, and it does not say who may use one.{src('fspfaq')}</li>
<li>A park page that only says a dump station exists, and does not say who may use it, is not in the table. Stations this guide already quoted from an operator page stay on the <a href="/">regional lists</a>.</li>
<li>The quoted rules on this page do not come from OpenStreetMap or another community listing. The map uses OpenStreetMap tiles. Each pin is a street address from that park's own page, matched by OpenStreetMap Nominatim.</li>
</ul>
</div>
<h2>Sources read on 27 October 2026</h2>
<div class="card"><ul>
<li><a href="{S['fspfee']}" rel="noopener">Florida State Parks fee schedule</a> (file name includes 2021_05_10) and the <a href="{S['fspfee2']}" rel="noopener">05.2022 copy</a></li>
<li><a href="{S['fspfee2013']}" rel="noopener">Fee schedule file whose name includes 2013_10_01</a></li>
<li><a href="{S['s258014']}" rel="noopener">Section 258.014, Florida Statutes</a> (2026)</li>
<li><a href="{S['fspcamp']}" rel="noopener">Florida State Parks camping page</a> and <a href="{S['fspfaq']}" rel="noopener">FAQ</a></li>
<li><a href="{S['anastasia']}" rel="noopener">Anastasia</a> amenities and <a href="{S['anastasiah']}" rel="noopener">hours</a></li>
<li><a href="{S['bluespring']}" rel="noopener">Blue Spring</a> amenities and <a href="{S['bluespringh']}" rel="noopener">hours</a></li>
<li><a href="{S['collier']}" rel="noopener">Collier-Seminole</a> amenities, <a href="{S['collierh']}" rel="noopener">hours</a>, and <a href="https://www.floridastateparks.org/parks-and-trails/collier-seminole-state-park" rel="noopener">park page</a></li>
<li><a href="{S['caverns']}" rel="noopener">Florida Caverns</a> amenities and <a href="{S['cavernsh']}" rel="noopener">hours</a></li>
<li><a href="{S['fortclinch']}" rel="noopener">Fort Clinch</a> amenities and <a href="{S['fortclinchh']}" rel="noopener">hours</a></li>
<li><a href="{S['gamble']}" rel="noopener">Gamble Rogers</a> amenities and <a href="{S['gambleh']}" rel="noopener">hours</a></li>
<li><a href="{S['kissimmee']}" rel="noopener">Kissimmee Prairie hours and fees</a></li>
<li><a href="{S['koreshan']}" rel="noopener">Koreshan hours and fees</a></li>
<li><a href="{S['littlet']}" rel="noopener">Little Talbot Island</a> amenities and <a href="{S['littleth']}" rel="noopener">hours</a></li>
<li><a href="{S['oscar']}" rel="noopener">Oscar Scherer hours and fees</a></li>
<li><a href="{S['manateehome']}" rel="noopener">Manatee Springs park page</a> and <a href="{S['manatee']}" rel="noopener">amenities</a></li>
</ul></div>
<p><a href="/fees/">Fees and access</a> | <a href="/rules/">Dumping rules</a> | <a href="/">Stations by region</a></p>'''
page('state-parks/index.html',"Florida State Park dump stations: access, fees, hours",sp,"Who may use a Florida State Park RV dump station, the published fee for a non-registered camper, and park pages that state another amount or a closure.",SP,crumbs=[("Home",BASE+"/"),("State park dumps",BASE+"/state-parks/")])
RULES_D="26 October 2026"
rb=f"""<h1>Where you can and cannot dump RV waste in Florida</h1>
<p>Florida law limits where a recreational vehicle may empty black water, grey water, or any other liquid waste. This page quotes the statute, the Department of Health park rule, the Florida Litter Law, the sanitary-nuisance statute, the pollution statute, and the FDOT rest-area rule. It is an unofficial reading of those public texts, not legal advice and not a statement by any agency. Read the linked sections.</p>
<p>The facts on this page come from the official sources linked below. This page does not use OpenStreetMap or any other community listing.</p>
{CALL}
<h2>Emptying an RV tank</h2>
<div class="card">
<p>Section 513.08(1), Florida Statutes, says: "It is unlawful to empty any receptacle or fixture containing human excreta, human urine, or any other liquid waste from a mobile home or recreational vehicle or at a recreational campsite except into a sewerage system approved by the department."</p>
<p>The prohibition is not limited to the toilet tank. It covers any other liquid waste from the recreational vehicle, which includes what travelers usually call grey water.</p>
<p>Section 513.08(2) says the operator or permittee of a mobile home park, lodging park, recreational vehicle park, or recreational camp shall provide the means for emptying those receptacles, and for cleaning them, as specified in the rules of the department.</p>
<p>Section 513.01(1) defines "Department" for this chapter as the Department of Health, including its representative county health departments.{src('s51308','s51301')}</p>
</div>
<h2>What a lawful park dump station is</h2>
<div class="card">
<p>Rule 64E-15.004, Florida Administrative Code (Sewage Disposal), is the Department of Health rule for sewage at mobile home parks, lodging parks, recreational vehicle parks, and recreational camps. The Florida Administrative Code record lists that rule as last amended effective 30 December 2009. The wording below is from the Department of Health copy of Chapter 64E-15 posted by the Glades County health department. Its history note matches the Florida Administrative Code record.{src('r64e15004','r64e15pdf')}</p>
<p>Subsection (1) requires a safe method of sewage collection, disposal, or treatment and disposal at each park or camp, in compliance with either Chapter 64E-6, F.A.C., Standards for Onsite Sewage Treatment and Disposal Systems, or Chapter 62-600, F.A.C., Domestic Wastewater Facilities. Chapter 62-600 is a Department of Environmental Protection chapter. The Florida Administrative Code entry for Rule 64E-6.001 is titled "General (Transferred)", and its history note says "Transferred to 62-6.001." Chapter 62-6 is the Department of Environmental Protection chapter with the same title, Standards for Onsite Sewage Treatment and Disposal Systems. Rule 64E-15.004, as posted in the Department of Health copy, still names Chapter 64E-6.{src('c64e6','r64e6001','c626','c62600')}</p>
<p>Rule 64E-15.001(10) defines "Sanitary Dump Station" as "a properly designed facility used for receiving and disposing of liquid wastes from recreational vehicle holding tanks." That definitions rule is listed as effective 20 May 1996. Subsection (11) defines a self-contained unit as a recreational vehicle which has a flush toilet, bathtub or shower, handwashing compartment, and internal storage compartments of potable water supply and sewage holding.{src('r64e15001','r64e15pdf')}</p>
<p>Rule 64E-15.004(5) says: "All recreational vehicle parks shall be provided with at least one easily accessible sanitary dump station for the use of occupants or patrons." Parks constructed after the effective date of the rule must provide a sanitary dump station for each 100 spaces, or fraction thereof, or for each 250 spaces, or fraction thereof, when more than fifty percent of the spaces have sewage disposal hookups.</p>
<p>Subsection (6) says a sanitary dump station shall consist of a trapped four inch sewer riser pipe connected to an approved sewage system, surrounded at the inlet end by a concrete apron sloped to the drain, with a suitably sized and hinged cover. A wash-down water outlet must be protected from backflow and back-siphonage.</p>
<p>Subsection (7) requires a sign immediately adjacent to the wash-down hose, in letters of at least three inches height, reading: WATER NOT SAFE FOR DRINKING.</p>
<p>Subsection (4) says the connection point for all sewer outlets shall be tightly capped when not in use.</p>
<p>There is a written exemption. Rule 64E-15.005(6), listed as amended effective 7 June 2007, says that if a park owner files a letter with the county health department stating the park has a potable water and sewer hook-up at each site and the park only rents to self-contained recreational vehicles, the park is exempt from the dump-station requirements in subsections 64E-15.004(5), (6), and (7).{src('r64e15005','r64e15pdf')}</p>
</div>
<h2>Ground, ditches, storm drains, and open water</h2>
<div class="card">
<p>Section 403.413 is the Florida Litter Law. Subsection (5) says that unless otherwise authorized by law or permit, it is unlawful for any person to dump raw human waste from any train, aircraft, motor vehicle, or vessel upon the public or private lands or waters of the state. Subsection (2) defines "dump" to include drain, discharge, or dispose of. The same subsection defines "motor vehicle" to include an automobile, truck, trailer, semitrailer, and any other vehicle that is powered by a motor.{src('s403413')}</p>
<p>Section 403.413(6)(j) says any person who violates subsection (5) is guilty of a misdemeanor of the second degree, punishable as provided in section 775.082 or section 775.083. Section 775.082(4)(b) provides a definite term of imprisonment not exceeding 60 days for a second-degree misdemeanor. Section 775.083(1)(e) says that fine shall not exceed $500. The same litter-law paragraph says that any person who dumps more than 500 pounds or more than 100 cubic feet of raw human waste, or who dumps any quantity of such waste for commercial purposes, is guilty of a felony of the third degree. Section 775.082(3)(e) provides a term of imprisonment not exceeding 5 years for a third-degree felony, and section 775.083(1)(c) says that fine shall not exceed $5,000. Paragraphs (1)(f) and (1)(g) of section 775.083 allow a higher amount equal to double the gain or the loss, or a higher amount a statute specifically authorizes. Subsection (5) uses the words "raw human waste." It does not use the words "grey water."{src('s403413','s775082','s775083')}</p>
<p>Section 386.041(1)(a) says untreated or improperly treated human waste, when existing, permitted, maintained, kept, or caused by any individual, municipal organization, or corporation, governmental or private, shall constitute prima facie evidence of maintaining a nuisance injurious to health. Section 386.01 defines a sanitary nuisance as the commission of any act, or the keeping, maintaining, propagation, existence, or permission of anything, by which the health or life of a person may be threatened or impaired, or by which or through which, directly or indirectly, disease may be caused. Section 386.051 says any person found guilty of creating, keeping, or maintaining a nuisance injurious to health shall be guilty of a misdemeanor of the second degree, punishable as provided in section 775.082 or section 775.083.{src('s386041','s38601','s386051')}</p>
<p>Section 403.161(1)(a) is the general pollution prohibition. It is not written only for recreational vehicles. It prohibits any person from causing pollution, except as otherwise provided in that chapter, so as to harm or injure human health or welfare, animal, plant, or aquatic life, or property. Subsection (3) says a person who willfully commits that violation commits a felony of the third degree, by a fine of not more than $50,000 or by imprisonment for 5 years, or both, for each offense. Subsection (4) says a violation of paragraph (1)(a) from reckless indifference or gross careless disregard is a misdemeanor of the second degree, by a fine of not more than $10,000 or by 60 days in jail, or both, for each offense.{src('s403161')}</p>
<p>None of these sections names a storm drain, a roadside ditch, or bare ground as an approved place to empty an RV tank.</p>
</div>
<h2>FDOT rest areas, welcome centers, and service plazas</h2>
<div class="card">
<p>FDOT Rule 14-28.002, F.A.C., effective 5 December 2018, is titled Public Use of Rest Areas and Welcome Centers, Truck Comfort Stations, and Wayside Parks. The rule text posted by FDOT does not mention a sanitary dump station. It prohibits camping. Parking at rest areas and welcome centers is limited to three hours, except for commercial motor vehicle operators and persons permitted under Rule 14-28.005. For commercial motor vehicle operators subject to hours-of-service regulations, parking is limited to ten hours. The rule says no person shall hook up a vehicle to electrical and water outlets. Bottles, broken glass, ashes, waste paper, or other rubbish shall be left only at places provided for disposal.{src('r1428','r1428pdf')}</p>
<p>On 26 October 2026 the Florida Department of Transportation rest area information page did not mention dump stations. It repeats the three-hour stay and the ban on overnight camping. The public rest-facility list is built from the Florida Department of Transportation map service fdotRestFacilities, layer fdotAMFacilities. That layer's amenity fields are Full Facility, Nighttime Security, Family Restroom, Adult Changing Table, Fenced Dog Area, Sun Pass Kiosk, Vending Machines, and ATM (automated teller machine). There is no dump-station field. The facility-list page filter offers Full Facilities, Nighttime Security, Family Restrooms, Adult Changing Tables, Dog Park Areas, Sun Pass Kiosks, Vending Machines, and ATMs (automated teller machines). It does not offer a dump station.{src('fdot','fdotlist','fdotgis')}</p>
</div>
<h2>When no dump station is close</h2>
<div class="card"><ol>
<li>Keep black water and grey water in the holding tanks until you reach a sewerage system approved by the Department of Health. Section 513.08 does not allow any other emptying. Section 403.413(5) separately prohibits dumping raw human waste from a motor vehicle onto the lands or waters of the state unless authorized by law or permit.</li>
<li>If you are a guest at a permitted recreational vehicle park, ask the office where occupants empty tanks. Section 513.08(2) puts that duty on the operator. If the site has a sewer connection, Rule 64E-15.004(3) says the connection shall be self draining and leak proof from liquids and gases and be connected by means of a readily removable, acid resistant material. Subsection (4) says the connection point for all sewer outlets shall be tightly capped when not in use. A park can be exempt from a separate dump station only when the owner has filed the full-hookup letter described in Rule 64E-15.005(6).</li>
<li>Inside a park or camp, Rule 64E-15.004(1) allows a transportable wastewater container or a cassette-type toilet only on the conditions in that subsection. The container must be specifically designed and sold for holding and transporting wastewater, with a tight-capping lid and watertight connections that under normal use will not leak or spill. Waste from hand washing sinks, kitchen sinks, and showers may go into a transportable wastewater container. Toilet waste may not. A cassette-type portable toilet may hold toilet waste if the storage container can be sealed so it will not leak or spill during transportation. Both must be transported to an approved disposal site without leakage, spillage, or a sanitary nuisance. If waste spills on the ground, the person transporting the tank shall immediately notify park management. The rule makes park managers responsible for enforcement and requires a disinfection protocol on file. It does not name a roadside, a rest area, or a storm drain as an approved disposal site.</li>
<li>Drive to a dump station that discharges to an approved system, and call ahead. Regional lists on this site separate official operator pages from community points. Many Florida State Parks pages describe the station as a campground amenity and do not say that a day visitor may use it. Anastasia State Park says: "A communal dump station is free for park campers."{src('anastasia')} Parks that do state a rule are quoted on the <a href="/state-parks/">state park dump</a> page.</li>
<li>The statutes and rules quoted on this page do not describe a statewide mobile pump-out for a traveler stopped on the roadside. They also do not authorize emptying a tank on the ground while waiting.</li>
</ol>
<p><a href="/">Stations by region</a> | <a href="/fees/">Fees and who can use a station</a></p>
</div>
<h2>Official sources read on 26 October 2026</h2>
<div class="card"><ul>
<li><a href="{S['s51308']}" rel="noopener">Section 513.08, Florida Statutes, Disposal of sewage</a> (2026)</li>
<li><a href="{S['s51301']}" rel="noopener">Section 513.01, Florida Statutes, Definitions</a>, including "Department"</li>
<li><a href="{S['r64e15004']}" rel="noopener">Rule 64E-15.004, F.A.C., Sewage Disposal</a> (effective 30 December 2009)</li>
<li><a href="{S['r64e15001']}" rel="noopener">Rule 64E-15.001, F.A.C., Definitions</a> (effective 20 May 1996)</li>
<li><a href="{S['r64e15005']}" rel="noopener">Rule 64E-15.005, F.A.C., Sanitary Facilities</a> (amended effective 7 June 2007)</li>
<li><a href="{S['r64e15pdf']}" rel="noopener">Chapter 64E-15 text, Department of Health copy</a> posted by the Glades County health department</li>
<li><a href="{S['c64e6']}" rel="noopener">Chapter 64E-6, F.A.C.</a> and <a href="{S['r64e6001']}" rel="noopener">Rule 64E-6.001 (Transferred)</a></li>
<li><a href="{S['c626']}" rel="noopener">Chapter 62-6, F.A.C., Standards for Onsite Sewage Treatment and Disposal Systems</a> (Department of Environmental Protection)</li>
<li><a href="{S['c62600']}" rel="noopener">Chapter 62-600, F.A.C., Domestic Wastewater Facilities</a> (Department of Environmental Protection)</li>
<li><a href="{S['s403413']}" rel="noopener">Section 403.413, Florida Statutes, Florida Litter Law</a></li>
<li><a href="{S['s403161']}" rel="noopener">Section 403.161, Florida Statutes, Prohibitions, violation, penalty, intent</a></li>
<li><a href="{S['s38601']}" rel="noopener">Section 386.01, Florida Statutes, Sanitary nuisance</a></li>
<li><a href="{S['s386041']}" rel="noopener">Section 386.041, Florida Statutes, Nuisances injurious to health</a></li>
<li><a href="{S['s386051']}" rel="noopener">Section 386.051, Florida Statutes, penalty</a></li>
<li><a href="{S['s775082']}" rel="noopener">Section 775.082, Florida Statutes, Penalties</a> and <a href="{S['s775083']}" rel="noopener">section 775.083, Fines</a></li>
<li><a href="{S['r1428']}" rel="noopener">Rule 14-28.002, F.A.C.</a> and the <a href="{S['r1428pdf']}" rel="noopener">FDOT copy of the rule text</a> (effective 5 December 2018)</li>
<li><a href="{S['fdot']}" rel="noopener">FDOT rest area information</a>, <a href="{S['fdotlist']}" rel="noopener">rest facility list</a>, and <a href="{S['fdotgis']}" rel="noopener">fdotRestFacilities map layer</a></li>
<li><a href="{S['anastasia']}" rel="noopener">Anastasia State Park experiences and amenities</a></li>
</ul></div>"""
page('rules/index.html',"Where you can and cannot dump RV wastewater in Florida",rb,"Florida statute, the Department of Health park rule, the Litter Law and the FDOT rest-area rule on where an RV may empty wastewater.",RULES_D,crumbs=[("Home",BASE+"/"),("Dumping rules",BASE+"/rules/")])
db='''<h1>Disclaimer</h1>
<h2>Accuracy</h2>
<p>Station names, locations, fees, access, hours and legal quotations on this site are taken from the linked public sources. They can be incomplete, misread or out of date. A source page can change after the date shown as last checked. Community map points can be missing, duplicated or in the wrong place.</p>
<h2>No warranty</h2>
<p>The site is provided for general information only, without any warranty of accuracy, completeness, timeliness or fitness for a particular purpose.</p>
<h2>Limitation of liability</h2>
<p>Nothing here is legal or professional advice, and we accept no liability for decisions made using it. That includes decisions about travel, where to empty a tank, fees, access, or how to read a statute or rule.</p>
<h2>External links are not endorsements</h2>
<p>Links to operator pages, statutes, agency rules and OpenStreetMap are provided so the source can be read. A link does not endorse that organization, and this site does not control those pages or later changes on them.</p>
<h2>Not affiliated</h2>
<p>This independent site is not affiliated with any government or agency. It is not affiliated with Florida State Parks, the Florida Department of Transportation (FDOT), the Florida Department of Health, the Florida Department of Environmental Protection, Love's or OpenStreetMap.</p>
<h2>Check official sources</h2>
<p>Always confirm with the official source or the facility before you act. Hours, fees, gate codes and who may use a station change, and many park stations are for registered campers only.</p>
<h2>Contact and corrections</h2>
<p>This site does not publish a contact email or a correction form. To check a listing, open the source link on that row and confirm it with the facility. Each page shows the date it was last checked.</p>
<p><a href="/">Stations by region</a> | <a href="/fees/">Fees and access</a> | <a href="/rules/">Dumping rules</a></p>'''
page('disclaimer/index.html',"Full disclaimer for this Florida RV dump station guide",db,"Disclaimer for this independent Florida RV dump station guide: accuracy, no warranty, liability limits, external links, affiliation and official sources.",NEW,crumbs=[("Home",BASE+"/"),("Disclaimer",BASE+"/disclaimer/")])
find_bits=['<h2>Home</h2><ul class="topic-list"><li data-keywords="'+H.escape(KW.get("index.html",""))+'">'+jump("index.html")+'</li></ul>']
for g,items in GROUPS:
    lis=''.join(f'<li data-keywords="{H.escape(KW.get(p,""))}">{jump(p)}</li>' for p,_t in items)
    find_bits.append(f'<h2>{H.escape(g)}</h2><ul class="topic-list">{lis}</ul>')
find_body='<h1>All pages</h1><p>Every page on this guide, grouped by topic. Use the search box to narrow this list. Clear the search to show every page.</p><p id="index-status" class="index-status" role="status">Showing every page.</p>'+''.join(find_bits)
page('find/index.html',"Find every page in this Florida RV dump station guide",find_body,"Search and browse every page in this independent Florida RV dump station guide, grouped by topic, including regions, fees, rules and the disclaimer.",crumbs=[("Home",BASE+"/"),("All pages",BASE+"/find/")])
nb='''<h1>Page not found</h1>
<p>That address is not a page on this guide.</p>
<ul class="grid">
<li><a href="/">Home</a></li>
<li><a href="/regions/panhandle/">Panhandle</a></li>
<li><a href="/regions/north/">North Florida</a></li>
<li><a href="/regions/central/">Central Florida</a></li>
<li><a href="/regions/tampa-bay-southwest/">Tampa Bay and Southwest</a></li>
<li><a href="/regions/southeast-keys/">Southeast and Keys</a></li>
<li><a href="/fees/">Fees and access</a></li>
<li><a href="/state-parks/">State park dumps</a></li>
<li><a href="/rules/">Dumping rules</a></li>
<li><a href="/find/">All pages</a></li>
<li><a href="/disclaimer/">Disclaimer</a></li>
</ul>'''
page('404.html',"Page not found on this Florida RV dump station guide",nb,"That page is not on this Florida RV dump station guide. Open the home page, a region, fees and access, dumping rules or the disclaimer.",NEW,crumbs=[("Home",BASE+"/"),("Page not found",BASE+"/404/")],article=False,robots="noindex")
assets()
pages=[os.path.relpath(os.path.join(dp,f),OUT) for dp,_,fs in os.walk(OUT) for f in fs if f.endswith('.html')]
open(os.path.join(OUT,'robots.txt'),'w').write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
listed=sorted(p for p in pages if p!='404.html')
open(os.path.join(OUT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}/{p.replace("index.html","")}</loc><lastmod>{SM[p]}</lastmod></url>\n' for p in listed)+'</urlset>\n')
verify_site()
print(len(recs),'records;',noff,'official;',ncom,'community;',cnt,'meta length warnings:',WARNS)
print('MAP REPORT')
for name,total,pins in MAP_REPORT:
    print(f'  {name}: {pins} pins / {total} locations')
print('STATIONS WITHOUT A PIN')
for x in recs:
    if x.get('lat') is None:
        print(' ', x['id'], x['name'])
print('STATIONS WITHOUT DIRECTIONS')
for x in recs:
    if not x.get('directions_address'):
        print(' ', x['id'], x['name'])
print('STATE PARKS WITHOUT A PIN')
for item in STATE_PARKS:
    if not item.get('map_pin'):
        print(' ', item['id'], item['name'], PLACES[item['place']].get('why'))
