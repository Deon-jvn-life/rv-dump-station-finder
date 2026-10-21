# Florida RV Dump Stations (static site)

Plain-HTML list of Florida RV dump stations by region, with fee, access, water, hours, source link and verification level on every row.

- `tools/official.json`: stations confirmed on operator pages (Florida State Parks experiences-amenities pages, Love's location pages).
- `tools/osm.json`: raw Overpass API result for amenity=sanitary_dump_station in Florida (community data, ODbL). `tools/osm_enriched.json` adds Nominatim reverse geocoding (road, city, county).
- `tools/checked_no_dump.json`: sources checked that do not state a dump station (FDOT rest areas, some parks with full hookups).
- `tools/build.py`: generator. Run `python3 tools/build.py` from the repo root; output in `site/`. Also writes `tools/stations_merged.json`.
- `vercel.json`: static, no build. Set `BASE` in build.py to the real domain before deploying.

Refresh OSM: POST to https://overpass-api.de/api/interpreter with
`[out:json];area["ISO3166-2"="US-FL"]->.a;nwr["amenity"="sanitary_dump_station"](area.a);out center tags;`

Last checked: 21 October 2026. Always call ahead.
