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

### Source formatting
Koristim `black` za formatiranje source koda i `isort`
za organizaciju importova kroz `pre-commit` framework
čija se konfiguracija nalazi u `.pre-commit-config.yaml`.
Taj alat se automatski pokreće na commit, no može se i
eksplicitno pokrenuti sa:
```bash
pre-commit run -a
```
