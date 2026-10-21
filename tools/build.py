#!/usr/bin/env python3
"""Build the Florida RV dump stations static site from JSON in tools/ into site/."""
import json,os,re,html as H,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,'site')
D="21 October 2026"; BASE="https://rv-dump-station-finder.vercel.app"  # replace with real domain before deploy
S=dict(fsp="https://www.floridastateparks.org/stay-night",fdot="https://www.fdot.gov/maintenance/rest-area-app/restareainfo.shtm",
 fdotlist="https://www.fdot.gov/maintenance/rest-area-app/rest-facilities-list",osm="https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dsanitary_dump_station",
 osmc="https://www.openstreetmap.org/copyright",overpass="https://overpass-api.de/",fspres="https://www.floridastateparks.org/stay-night",
 rainbow="https://www.floridastateparks.org/parks-and-trails/rainbow-springs-state-park/experiences-amenities",
 anastasia="https://www.floridastateparks.org/parks-and-trails/anastasia-state-park/experiences-amenities",loves="https://www.loves.com/locations")
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
def page(path,title,body,desc):
    depth=path.count('/'); r='../'*depth
    nav=f'<a href="{r}index.html">Home</a>'+''.join(f'<a href="{r}regions/{k}/index.html">{n}</a>' for k,(n,_) in REG.items())+f'<a href="{r}fees/index.html">Fees</a>'
    h=f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H.escape(title)}</title><meta name="description" content="{H.escape(desc)}"><link rel="canonical" href="{BASE}/{path.replace('index.html','')}"><style>{CSS}</style><script defer src="/_vercel/insights/script.js"></script></head><body>
<header><a href="{r}index.html">Florida RV Dump Stations</a><nav>{nav}</nav></header><main><p class="checked">Last checked: {D}</p>{body}</main>
<footer>Independent, unofficial guide. Not affiliated with Florida State Parks, FDOT, Love's or OpenStreetMap. Official listings are linked to the operator page they came from. Community listings come from OpenStreetMap contributors (data &copy; OpenStreetMap contributors, ODbL){src('osmc')}. Dump stations close, change rules and charge new fees without notice: always call ahead. Last checked: {D}.</footer></body></html>'''
    assert '\u2014' not in h and '\u2013' not in h, path
    p=os.path.join(OUT,path); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(h)
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
faq=[("Can I dump at a Florida interstate rest area?",f"Not according to any FDOT page we checked. The FDOT rest area page and facility list do not mention dump stations, and FDOT says overnight camping is not permitted and visitors may stay up to three hours{src('fdot','fdotlist')}. Some third-party apps list rest area dumps; we could not confirm those on an official source."),
("Can I use a state park dump station if I am not camping there?",f"Usually not stated. Anastasia State Park says its communal dump station is free for park campers{src('anastasia')}. Other park pages we read do not say whether day visitors may dump. Ask the ranger station first."),
("Do I need a gate code?",f"At some parks, yes. Rainbow Springs says its campground gates are closed at all times and the code is given on your day of arrival{src('rainbow')}."),
("Are OpenStreetMap entries reliable?",f"They are community data{src('osm')}. Many Florida entries have no name, fee or access tags. We show them so you know where to look, flagged as Community, and they need a phone call to confirm."),
("Is there potable water at the dump?","Rarely stated by official sources. Where an OSM contributor tagged water_point we show it as an OSM tag. Never use the rinse hose for drinking water."),
("How current is this?",f"All records were collected on {D}. Each row links to its source so you can recheck.")]
body=f'''<h1>Florida RV dump stations: sourced list by region</h1>
<p>A plain list of places in Florida where an RV can empty black and grey tanks, taken only from operator pages (Florida State Parks, Love's) and OpenStreetMap community data. {len(recs)} stations on {D}: {noff} confirmed on an official page, {ncom} community-mapped.</p>{CALL}
<h2>Pick a region</h2><ul class="grid">'''+''.join(f'<li><a href="regions/{k}/index.html">{n}</a> ({cnt[k]} stations)</li>' for k,(n,_) in REG.items())+f'''</ul>
<p><a href="fees/index.html">Dump station fees and who can use them</a></p>
<h2>How to use a dump station</h2><div class="card"><ol><li>Pull up so your sewer outlet is on the drain side. Set the parking brake.</li><li>Wear disposable gloves. Connect the sewer hose to your outlet first, then put the other end fully into the drain inlet and secure it.</li><li>Open the black tank valve first and let it empty completely.</li><li>Close it, then open the grey tank valve. Grey water helps flush the hose.</li><li>Close the valves, rinse the hose with the non-potable rinse water if provided, and drain it into the inlet.</li><li>Disconnect at the RV end first, rinse the area, and close the drain lid.</li></ol>
<p class="src">General practice guidance, not from a single official source. Always follow posted signs at the station.</p></div>
<h2>Etiquette</h2><div class="card"><ul><li>Be quick when others are waiting. Do tank flushing and hose cleaning at your site if you can.</li><li>Never use the rinse hose to fill your fresh water tank.</li><li>Leave the pad cleaner than you found it.</li><li>Pay any posted fee and respect campers-only signs.</li><li>Do not dump grey or black water anywhere other than an approved inlet. It is a health hazard.</li></ul></div>
{LEVELS}
<h2>Checked, no dump station stated</h2><div class="card"><ul>'''+''.join(f'<li><strong>{H.escape(c["name"])}</strong>: {H.escape(c["note"])} <span class="src">[<a href="{c["source"]}" rel="noopener">source</a>]</span></li>' for c in checked)+'''</ul></div>
<h2>Short FAQ</h2>'''+''.join(f'<div class="card"><strong>{q}</strong><p>{a}</p></div>' for q,a in faq)
if os.path.exists(OUT): shutil.rmtree(OUT)
page('index.html',"Florida RV dump stations by region: sourced list",body,"Florida RV dump stations from Florida State Parks, Love's and OpenStreetMap, by region, with fees, access and source links.")
for k,(n,cs) in REG.items():
    rows=[x for x in recs if x['region']==k]
    b=f'<h1>RV dump stations: {n}</h1><p>{len(rows)} stations. Counties in this region: {", ".join(c.replace("_"," ") for c in cs.split())}.</p>{CALL}'+table(rows)+LEVELS+'<p><a href="../../index.html">All regions</a> | <a href="../../fees/index.html">Fees</a></p>'
    page(f'regions/{k}/index.html',f"RV dump stations in {n}, Florida",b,f"RV dump stations in the {n} region of Florida with fees, access and sources.")
fr=[x for x in recs if x['fee']!='Not stated by source']
fb=f'''<h1>Florida RV dump station fees and access</h1><p>Most sources do not publish a dump fee. Below are the only fee statements we found, then a summary of access rules.</p>{CALL}
<h2>Fees that a source states</h2><div class="wrap"><table><tr><th>Station</th><th>County</th><th>Fee</th><th>Who can use it</th><th>Verification</th></tr>'''+''.join(f'<tr><td>{H.escape(x["name"])}</td><td>{x["county"]}</td><td>{H.escape(x["fee"])}</td><td>{H.escape(x["access"])}</td><td>{x["level"]} <span class="src">[<a href="{x["source"]}" rel="noopener">source</a>]</span></td></tr>' for x in fr)+f'''</table></div>
<p>{len(recs)-len(fr)} of {len(recs)} stations: fee not stated by source.</p>
<h2>Access summary</h2><div class="card"><ul>
<li>Florida State Parks dump stations are described as campground amenities. Anastasia says free for park campers{src('anastasia')}. Day-visitor use is not stated on the other park pages we read. State park camping reservations: 800-326-3521{src('fspres')}.</li>
<li>Love's lists RV Dump Service among amenities at the four Florida locations we checked; price not stated on the location page{src('loves')}.</li>
<li>FDOT rest areas: no dump stations stated{src('fdot')}.</li>
<li>OpenStreetMap access tags: {sum(1 for x in recs if x['access'].startswith('Customers'))} customers only, {sum(1 for x in recs if x['access'].startswith('Public'))} public, rest not stated{src('osm')}.</li></ul></div>'''
page('fees/index.html',"Florida RV dump station fees and access rules",fb,"Which Florida RV dump stations state a fee, and who may use them, with sources.")
pages=[os.path.relpath(os.path.join(dp,f),OUT) for dp,_,fs in os.walk(OUT) for f in fs if f.endswith('.html')]
open(os.path.join(OUT,'robots.txt'),'w').write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(os.path.join(OUT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{BASE}/{p.replace("index.html","")}</loc><lastmod>2026-10-21</lastmod></url>\n' for p in sorted(pages))+'</urlset>\n')
print(len(recs),'records;',noff,'official;',ncom,'community;',cnt)
