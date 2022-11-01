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
grep -vx -f schema.sql database.sql > data.sql
```

### Brisanje sheme
```bash
lab schema drop
```
