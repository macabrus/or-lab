# Skup podataka o biljkama
Ovaj skup podataka sadrži informacije o biljkama i nekim njihovim svojstvima:
- `species` - latinski naziv vrste
- `genus` - latinski naziv roda biljke
- `petal_count` - broj latica cvjetova biljke
- `soil_ph_min` - minimalni pH zemlje kako bi biljka nesmetano rasla
- `soil_ph_max` - maksimalni pH tla kako bi biljka nesmetano rasla
- `temp_min` - minimalna primjerena temperatura za nesmetani rast biljke
- `temp_max` - maksimalna primjerena temperatura za nesmetani rast biljke
- `lifespan_years` - prosječni životni vijek biljke izražen u godinama
- `is_edible` - istinosna vrijednost koja označava je li biljka jestiva za ljude
- `water_content` - decimalna vrijednost u rasponu od 0 do 1 koja označava prosječan udio vode u biljci

### Dokumentacija
OpenAPI dokumentacija backenda dostupna je u `docs/` direktoriju.
Korišten je predložak `https://github.com/swagger-api/swagger-ui`.
Možemo ju servirati i pregledavati u web pregledniku sa:
```bash
cd docs && python -m http.server 8000
```


### Pokretanje projekta
```bash
poetry shell
poetry install
lab schema init
lab data import

# Možemo provjeriti podatke u bazi sa:
sqlite3 -column -header test.db 'select * from plant'
```

### Izvoz podataka
```bash
lab data export -f data.json  # u JSON formatu
lab data export -f data.csv  # u CSV formatu

# izvoz podataka i sheme zajedno
sqlite3 test.db .dump > dump.sql

# izvoz samo sheme
sqlite3 test.db .schema > schema.sql

# izvoz podataka bez sheme
sqlite3 test.db .schema > schema.sql
sqlite3 test.db .dump > dump.sql
grep -vx -f schema.sql dump.sql > data.sql
```

### Brisanje sheme
```bash
lab schema drop
```

### Frontend i backend (TODO)
Potrebno je pripremiti production build frontenda:
```bash
cd frontend
npm i
npm build
cd ..
```

Flask će servirati SolidJS frontend/dist/ bundle folder kao statički content u web root (`/`). SolidJS će komunicirati s Flask API-jem preko `fetch` za dohvaćanje podataka.
Tada se može pokrenuti s:
```bash
lab web      # default port 80
lab web 8080 # specify port
```

### Autentifikacija
Možemo se prijaviti u autentifikaciju s Google računom (ili nekim od dostupnih providera)
kroz Auth0 OAuth2 shemu. Međutim, često OAuth2 provideri rade probleme s
portovima u domenama (brišu ih ili ignoriraju) te zahtjevaju jednostavan
naziv HTTP destinacije. Možemo taj problem rješiti s jednostavnim lokalnim
caddy reverse proxyjem koji prosljeđuje dekriptirane veze na stvarni lokalni
port našeg backenda:
```bash
caddy reverse-proxy --from 127.0.0.1:443 --to 127.0.0.1:8080
```
Za implementaciju je korištena vrlo jednostavna `authlib` python knjižnica koja
interno koristi `crpytography` za validaciju tokena.

### Kodiranje URI parametara
REST upite možemo testirati s `curl`. Parametre upita u URL-u
možemo kodirati u format koji backend očekuje s:
```bash
lab query encode '{"example": "json"}'
lab query decode eJyrVkqtSMwtyElVslJQyirOz1OqBQBCVwaB
```
Odlučio sam se za ovaj pristup sa kompresiranjem URI parametara
kako bi upiti i dalje ostali GET i očuvali semantičko značenje.
Pošto nije uobičajeno slati tijelo u GET upitima,
posegnuo sam za kompresijom URL parametara.
Filtriranje i paginacija podataka zapravo jest operacija čitanja (READ),
te ne mijenja podatke, te bi ona _trebala_ biti GET upit.
Operacije su i dalje idempotentne i _cacheable_
samo su URI manje razumljivi čitatelju.

### Testiranje REST sučelja
```bash
API="http://localhost:8080/api"
MIME="Content-Type: application/json"

echo --- Test fetch all ---
curl -s "$API/plant?size=100" | jq '[.[] | {id,name}]'

echo --- Test fetch by id ---
curl -s "$API/plant/1"

echo --- Test add new plant ---
CREATE='{"name": "Another Aloe"}'
curl -s -H "$MIME" -d "$CREATE" "$API/plant"

# fetch id of created plant
FILTER=$(lab query encode '{"name": "Another"}')
PLANT_ID=$(curl -s "$API/plant?filter=$FILTER" | jq '.[] | .id')

echo --- Test update plant ---
UPDATE='{"is_edible": true}'
curl -s -X PATCH -H "$MIME" -d "$UPDATE" "$API/plant/$PLANT_ID"
curl -s "$API/plant/$PLANT_ID" # check if updated

echo --- Test delete plant ---
curl -s -X DELETE "$API/plant/$PLANT_ID"
```

### Source formatting
Koristim `black` za formatiranje source koda i `isort`
za organizaciju importova kroz `pre-commit` framework
čija se konfiguracija nalazi u `.pre-commit-config.yaml`.
Taj alat se automatski pokreće na commit, no može se i
eksplicitno pokrenuti sa:
```bash
pre-commit run -a
```
