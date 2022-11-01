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
init-schema
import-data
```

### Izvoz podataka u JSON formatu
```bash
export-schema --json -f data.json
```

### Izvoz podataka u CSV formatu
```bash
export-schema --csv -f data.csv
```

### Brisanje sheme
```bash
drop-schema
```
