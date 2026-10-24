#!/usr/bin/env python3
"""Build the Florida RV dump stations static site from JSON in tools/ into site/."""
import json,os,re,html as H,shutil,sys,struct,zlib
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,'site')
D="21 October 2026"; BASE="https://rv-dump-station-finder.vercel.app"  # replace with real domain before deploy
# Optional search-console tokens. A blank value omits that meta tag.
VERIFY={"google-site-verification":"","msvalidate.01":""}
DISCLAIMER="For general information only. This independent site is not affiliated with any government or agency. Information can change and may contain errors; always confirm with the official source or facility before you act. Nothing here is legal or professional advice, and we accept no liability for decisions made using it."
NEW="24 October 2026"
S=dict(fsp="https://www.floridastateparks.org/stay-night",fdot="https://www.fdot.gov/maintenance/rest-area-app/restareainfo.shtm",
 fdotlist="https://www.fdot.gov/maintenance/rest-area-app/rest-facilities-list",osm="https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dsanitary_dump_station",
 osmc="https://www.openstreetmap.org/copyright",overpass="https://overpass-api.de/",fspres="https://www.floridastateparks.org/stay-night",
 rainbow="https://www.floridastateparks.org/parks-and-trails/rainbow-springs-state-park/experiences-amenities",
 anastasia="https://www.floridastateparks.org/parks-and-trails/anastasia-state-park/experiences-amenities",loves="https://www.loves.com/locations",
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
 fdotgis="https://gis.fdot.gov/arcgis/rest/services/fdotRestFacilities/MapServer/1")
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
recs=[]
for o in off: o['region']=region(o['county']); recs.append(o)
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
    recs.append(dict(id=f"osm-{e['id']}",name=nm,operator=t.get('operator','Not stated by source'),address=(road or 'Not stated by source'),city=place or 'Not stated by source',county=county,
      lat=e['lat'],lon=e['lon'],fee=fee,access=acc,water=wat,hours=t.get('opening_hours','Not stated by source'),notes='; '.join(extra),quote='',
      source=f"https://www.openstreetmap.org/node/{e['id']}",level="Community (OpenStreetMap)",region=region(county)))
json.dump(recs,open(os.path.join(HERE,'stations_merged.json'),'w'),indent=1)
CSS=open(os.path.join(HERE,'style.css')).read()
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
FAVICON='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><title>Florida RV Dump Stations</title><rect width="32" height="32" rx="7" fill="#0b4f6c"/><path fill="#ffffff" d="M16 5c-4.1 0-7.4 3.2-7.4 7.3 0 5.5 7.4 14.2 7.4 14.2s7.4-8.7 7.4-14.2C23.4 8.2 20.1 5 16 5zm0 10.2a2.9 2.9 0 1 1 0-5.8 2.9 2.9 0 0 1 0 5.8z"/></svg>\n'
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
    w,h=1200,630; teal=(0x0b,0x4f,0x6c); white=(255,255,255); mist=(0xd6,0xec,0xf5)
    buf=new_canvas(w,h,teal)
    draw_pin(buf,w,h,600,190,90,white,teal)
    draw_centered(buf,w,h,"FLORIDA RV DUMP STATIONS",410,6,white)
    draw_centered(buf,w,h,"SOURCED LIST BY REGION",478,4,mist)
    return w,h,buf
def render_icon():
    w=h=180; teal=(0x0b,0x4f,0x6c); buf=new_canvas(w,h,teal)
    draw_pin(buf,w,h,90,72,50, (255,255,255), teal)
    return w,h,buf
def assets():
    os.makedirs(OUT,exist_ok=True)
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
        for href in re.findall(r'href="([^"]*)"', text):
            if href.startswith('http://') or href.startswith('https://') or href.startswith('mailto:'): continue
            assert href.startswith('/') and 'index.html' not in href and not href.endswith('.html'), (rel, href)
        if VERIFY.get('google-site-verification'): assert VERIFY['google-site-verification'] in text
        else: assert 'google-site-verification' not in text
        if VERIFY.get('msvalidate.01'): assert VERIFY['msvalidate.01'] in text
        else: assert 'msvalidate.01' not in text
    sm=open(os.path.join(OUT,'sitemap.xml')).read()
    assert sm.count('<url>')==len(htmls)-1
    assert BASE+'/disclaimer/</loc>' in sm and '404' not in sm
    assert '<lastmod>2026-10-24</lastmod>' in sm
    assert sm.count('<lastmod>2026-10-22</lastmod>')==len(htmls)-2
    assert png_size(os.path.join(OUT,'og.png'))==(1200,630)
    assert png_size(os.path.join(OUT,'apple-touch-icon.png'))==(180,180)
    svg=open(os.path.join(OUT,'favicon.svg')).read()
    assert svg.strip().startswith('<svg') and '\u2014' not in svg and '\u2013' not in svg
def page(path,title,body,desc,checked=None,crumbs=None,article=True,faq=None,robots=None,sitemap=None):
    when=checked or D
    check_meta(path,title,desc)
    if not crumbs: raise SystemExit('missing breadcrumbs for '+path)
    canon=canon_for(path); SM[path]=sitemap or '2026-10-22'
    nav='<a href="/">Home</a>'+''.join(f'<a href="/regions/{k}/">{n}</a>' for k,(n,_) in REG.items())+'<a href="/fees/">Fees</a><a href="/rules/">Dumping rules</a>'
    blocks=[]
    if path=='index.html':
        blocks.append(website_ld(desc)); blocks.append(organization_ld())
    if article: blocks.append(article_ld(title,desc,canon,when))
    blocks.append(crumb_ld(crumbs))
    if faq: blocks.append(faq_ld(faq))
    og='article' if article and path not in ('index.html','404.html') else 'website'
    img=BASE+'/og.png'; e=H.escape
    head=['<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
          '<title>'+e(title)+'</title>','<meta name="description" content="'+e(desc)+'">','<link rel="canonical" href="'+e(canon)+'">',
          '<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
          '<meta property="og:type" content="'+og+'"><meta property="og:site_name" content="Florida RV Dump Stations"><meta property="og:locale" content="en_US">',
          '<meta property="og:title" content="'+e(title)+'"><meta property="og:description" content="'+e(desc)+'"><meta property="og:url" content="'+e(canon)+'">',
          '<meta property="og:image" content="'+img+'"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Florida RV Dump Stations">',
          '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+e(title)+'"><meta name="twitter:description" content="'+e(desc)+'"><meta name="twitter:image" content="'+img+'"><meta name="twitter:image:alt" content="Florida RV Dump Stations">']
    for name,val in VERIFY.items():
        if val: head.append('<meta name="'+e(name)+'" content="'+e(val)+'">')
    if robots: head.append('<meta name="robots" content="'+e(robots)+'">')
    head.extend(ld(b) for b in blocks)
    head.append('<style>'+CSS+'</style><script defer src="/_vercel/insights/script.js"></script></head><body>')
    foot=('<footer><p><a href="/">Home</a> | <a href="/fees/">Fees and access</a> | <a href="/rules/">Dumping rules</a> | <a href="/disclaimer/">Disclaimer</a></p>'
          '<p class="disclaimer">'+e(DISCLAIMER)+'</p><p>Independent, unofficial guide. Not affiliated with Florida State Parks, FDOT, the Florida Department of Health, the Florida Department of Environmental Protection, Love\'s or OpenStreetMap. Official listings are linked to the operator page they came from. Community listings come from OpenStreetMap contributors (data &copy; OpenStreetMap contributors, ODbL)'
          +src('osmc')+'. Dump stations close, change rules and charge new fees without notice: always call ahead. Last checked: '+e(when)+'.</p></footer>')
    h=''.join(head)+'<header><a href="/">Florida RV Dump Stations</a><nav>'+nav+'</nav></header><main><p class="checked">Last checked: '+e(when)+'</p><p class="disclaimer">'+e(DISCLAIMER)+'</p>'+body+'</main>'+foot+'</body></html>'
    assert '\u2014' not in h and '\u2013' not in h, path
    p=os.path.join(OUT,path); os.makedirs(os.path.dirname(p) or OUT, exist_ok=True); open(p,'w').write(h)
CALL='<div class="card note"><strong>Call ahead.</strong> Hours, fees, gate codes and who may use a station change often, and many park stations are for registered campers only. Confirm with the operator before you drive there.</div>'
def table(rows):
    t='<input id="q" placeholder="Filter by name, city or county" oninput="var v=this.value.toLowerCase();document.querySelectorAll(\'table tr\').forEach(function(r){if(r.querySelector(\'td\'))r.style.display=r.textContent.toLowerCase().indexOf(v)>-1?\'\':\'none\'})"><div class="wrap"><table><tr><th>Station</th><th>Address / city</th><th>Coordinates</th><th>Fee</th><th>Who can use it</th><th>Potable water</th><th>Hours / season</th><th>Verification</th></tr>'
    for x in sorted(rows,key=lambda x:(x['level'].startswith('Community'),x['county'],x['name'])):
        co=f'<a href="https://www.openstreetmap.org/?mlat={x["lat"]}&amp;mlon={x["lon"]}#map=17/{x["lat"]}/{x["lon"]}" rel="noopener">{x["lat"]:.5f}, {x["lon"]:.5f}</a>' if x['lat'] else 'Not stated by source'
        s=f'<a href="{x["source"]}" rel="noopener">source</a>'+(f', <a href="{x["source2"]}" rel="noopener">OSM</a>' if x.get('source2') else '')
        q=f'<br><span class="src">Source says: "{H.escape(x["quote"])}"</span>' if x['quote'] else ''
        n=f'<br><span class="src">{H.escape(x["notes"])}</span>' if x['notes'] else ''
        lv='ok' if x['level'].startswith('Official') else 'comm'
        t+=f'<tr><td><strong>{H.escape(x["name"])}</strong>{q}{n}</td><td>{H.escape(x["address"])}<br>{H.escape(x["city"])}, {H.escape(x["county"])} County</td><td>{co}</td><td>{H.escape(x["fee"])}</td><td>{H.escape(x["access"])}</td><td>{H.escape(x["water"])}</td><td>{H.escape(x["hours"])}</td><td><span class="lv {lv}">{x["level"]}</span> <span class="src">[{s}]</span></td></tr>'
    return t+'</table></div>'
LEVELS=f'''<div class="card"><strong>Verification levels</strong><ul><li><span class="lv ok">Official</span> the operator's own page (Florida State Parks, Love's) states a dump station, quoted in the table.</li>
<li><span class="lv ok">Official + OSM</span> official page plus an OpenStreetMap point that names the same operator, used only for coordinates and extra tags.</li>
<li><span class="lv comm">Community (OpenStreetMap)</span> mapped by volunteers as amenity=sanitary_dump_station{src('osm')}. Name, fee and access tags are often missing. Treat as a lead, not a confirmation.</li></ul></div>'''
cnt={k:sum(1 for x in recs if x['region']==k) for k in REG}
noff=sum(1 for x in recs if x['level'].startswith('Official')); ncom=len(recs)-noff
faq=[("Can I dump at a Florida interstate rest area?",f"Not according to any FDOT page we checked. The FDOT rest area page and facility list do not mention dump stations, and FDOT says overnight camping is not permitted and visitors may stay up to three hours{src('fdot','fdotlist')}. Some third-party apps list rest area dumps; we could not confirm those on an official source. The statute, the health rule, and the FDOT rest-area rule are on the <a href=\"/rules/\">dumping rules</a> page."),
("Can I use a state park dump station if I am not camping there?",f"Usually not stated. Anastasia State Park says its communal dump station is free for park campers{src('anastasia')}. Other park pages we read do not say whether day visitors may dump. Ask the ranger station first."),
("Do I need a gate code?",f"At some parks, yes. Rainbow Springs says its campground gates are closed at all times and the code is given on your day of arrival{src('rainbow')}."),
("Are OpenStreetMap entries reliable?",f"They are community data{src('osm')}. Many Florida entries have no name, fee or access tags. We show them so you know where to look, flagged as Community, and they need a phone call to confirm."),
("Is there potable water at the dump?","Rarely stated by official sources. Where an OSM contributor tagged water_point we show it as an OSM tag. Never use the rinse hose for drinking water."),
("How current is this?",f"All records were collected on {D}. Each row links to its source so you can recheck.")]
body=f'''<h1>Florida RV dump stations: sourced list by region</h1>
<p>A plain list of places in Florida where an RV can empty black and grey tanks, taken only from operator pages (Florida State Parks, Love's) and OpenStreetMap community data. {len(recs)} stations on {D}: {noff} confirmed on an official page, {ncom} community-mapped.</p>{CALL}
<h2>Pick a region</h2><ul class="grid">'''+''.join(f'<li><a href="/regions/{k}/">{n}</a> ({cnt[k]} stations)</li>' for k,(n,_) in REG.items())+f'''</ul>
<p><a href="/fees/">Dump station fees and who can use them</a></p>
<p><a href="/rules/">Where you can and cannot dump RV waste in Florida</a></p>
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
    b=f'<h1>RV dump stations: {n}</h1><p>{len(rows)} stations. Counties in this region: {", ".join(c.replace("_"," ") for c in cs.split())}.</p>{CALL}'+table(rows)+LEVELS+'<p><a href="/">All regions</a> | <a href="/fees/">Fees</a> | <a href="/rules/">Dumping rules</a></p>'
    rt,rd=REGION_SEO[k]
    page(f'regions/{k}/index.html',rt,b,rd,crumbs=[("Home",BASE+"/"),(n,BASE+f"/regions/{k}/")])
fr=[x for x in recs if x['fee']!='Not stated by source']
fb=f'''<h1>Florida RV dump station fees and access</h1><p>Most sources do not publish a dump fee. Below are the only fee statements we found, then a summary of access rules.</p>{CALL}
<h2>Fees that a source states</h2><div class="wrap"><table><tr><th>Station</th><th>County</th><th>Fee</th><th>Who can use it</th><th>Verification</th></tr>'''+''.join(f'<tr><td>{H.escape(x["name"])}</td><td>{x["county"]}</td><td>{H.escape(x["fee"])}</td><td>{H.escape(x["access"])}</td><td>{x["level"]} <span class="src">[<a href="{x["source"]}" rel="noopener">source</a>]</span></td></tr>' for x in fr)+f'''</table></div>
<p>{len(recs)-len(fr)} of {len(recs)} stations: fee not stated by source.</p>
<h2>Access summary</h2><div class="card"><ul>
<li>Florida State Parks dump stations are described as campground amenities. Anastasia says free for park campers{src('anastasia')}. Day-visitor use is not stated on the other park pages we read. State park camping reservations: 800-326-3521{src('fspres')}.</li>
<li>Love's lists RV Dump Service among amenities at the four Florida locations we checked; price not stated on the location page{src('loves')}.</li>
<li>FDOT rest areas: no dump stations stated{src('fdot')}.</li>
<li>OpenStreetMap access tags: {sum(1 for x in recs if x['access'].startswith('Customers'))} customers only, {sum(1 for x in recs if x['access'].startswith('Public'))} public, rest not stated{src('osm')}.</li></ul></div>
<p>For the statute and the Department of Health rule on where a tank may be emptied, see <a href="/rules/">where you can and cannot dump</a>.</p>'''
page('fees/index.html',"Florida RV dump station fees and access, with sources",fb,"Which Florida RV dump stations state a fee, who may use them, and how access is described on operator pages and OpenStreetMap tags.",crumbs=[("Home",BASE+"/"),("Fees",BASE+"/fees/")])
RULES_D="22 October 2026"
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
<p>On 22 October 2026 the FDOT rest area information page did not mention dump stations. It repeats the three-hour stay and the ban on overnight camping. The public rest-facility list is built from the FDOT map service fdotRestFacilities, layer fdotAMFacilities. That layer's amenity fields are Full Facility, Nighttime Security, Family Restroom, Adult Changing Table, Fenced Dog Area, Sun Pass Kiosk, Vending Machines, and ATM. There is no dump-station field. The facility-list page offers those same amenities in its filter and does not offer a dump station.{src('fdot','fdotlist','fdotgis')}</p>
</div>
<h2>When no dump station is close</h2>
<div class="card"><ol>
<li>Keep black water and grey water in the holding tanks until you reach a sewerage system approved by the Department of Health. Section 513.08 does not allow any other emptying. Section 403.413(5) separately prohibits dumping raw human waste from a motor vehicle onto the lands or waters of the state unless authorized by law or permit.</li>
<li>If you are a guest at a permitted recreational vehicle park, ask the office where occupants empty tanks. Section 513.08(2) puts that duty on the operator. If the site has a sewer connection, Rule 64E-15.004(3) says the connection shall be self draining and leak proof from liquids and gases and be connected by means of a readily removable, acid resistant material. Subsection (4) says the connection point for all sewer outlets shall be tightly capped when not in use. A park can be exempt from a separate dump station only when the owner has filed the full-hookup letter described in Rule 64E-15.005(6).</li>
<li>Inside a park or camp, Rule 64E-15.004(1) allows a transportable wastewater container or a cassette-type toilet only on the conditions in that subsection. The container must be specifically designed and sold for holding and transporting wastewater, with a tight-capping lid and watertight connections that under normal use will not leak or spill. Waste from hand washing sinks, kitchen sinks, and showers may go into a transportable wastewater container. Toilet waste may not. A cassette-type portable toilet may hold toilet waste if the storage container can be sealed so it will not leak or spill during transportation. Both must be transported to an approved disposal site without leakage, spillage, or a sanitary nuisance. If waste spills on the ground, the person transporting the tank shall immediately notify park management. The rule makes park managers responsible for enforcement and requires a disinfection protocol on file. It does not name a roadside, a rest area, or a storm drain as an approved disposal site.</li>
<li>Drive to a dump station that discharges to an approved system, and call ahead. Regional lists on this site separate official operator pages from community points. Many Florida State Parks pages describe the station as a campground amenity and do not say that a day visitor may use it. Anastasia State Park says: "A communal dump station is free for park campers."{src('anastasia')}</li>
<li>The statutes and rules quoted on this page do not describe a statewide mobile pump-out for a traveler stopped on the roadside. They also do not authorize emptying a tank on the ground while waiting.</li>
</ol>
<p><a href="/">Stations by region</a> | <a href="/fees/">Fees and who can use a station</a></p>
</div>
<h2>Official sources read on 22 October 2026</h2>
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
page('disclaimer/index.html',"Full disclaimer for this Florida RV dump station guide",db,"Disclaimer for this independent Florida RV dump station guide: accuracy, no warranty, liability limits, external links, affiliation and official sources.",NEW,crumbs=[("Home",BASE+"/"),("Disclaimer",BASE+"/disclaimer/")],sitemap="2026-10-24")
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
<li><a href="/rules/">Dumping rules</a></li>
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
