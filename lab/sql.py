from lab.models import Genus, Plant
from lab.utils import alias_map, columns, csv_placeholders, csv_props

INSERT_GENUS_SQL = f"""
INSERT INTO genus({csv_props(Genus, skip={'id', 'species'})})
VALUES ({csv_placeholders(Genus, skip={'id', 'species'})})
"""

INSERT_PLANT_SQL = f"""
INSERT INTO plant(genus_id, {csv_props(Plant, skip={'id'})})
VALUES (?, {csv_placeholders(Plant, skip={'id'})})
"""

SELECT_GENUS_PLANT_SQL = f"""
SELECT 
    {columns(Genus, table='g', alias=alias_map('g', Genus), skip={'species'})},
    {columns(Plant, table='p', alias=alias_map('p', Plant))}
FROM genus AS g
LEFT JOIN plant AS p
ON g.id = p.genus_id
"""

CREATE_GENUS = """
CREATE TABLE genus(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)"""

CREATE_PLANT = """
CREATE TABLE plant(
    id INTEGER PRIMARY KEY,
    genus_id INTEGER,
    name TEXT UNIQUE NOT NULL,
    petal_count INTEGER,
    lifespan_years REAL,
    soil_ph_min REAL,
    soil_ph_max REAL,
    temp_min REAL,
    temp_max REAL,
    is_edible BOOLEAN,
    water_content REAL,

    FOREIGN KEY (genus_id) REFERENCES genus(id) ON DELETE CASCADE
)"""

DROP_GENUS = "DROP TABLE genus"

DROP_PLANT = "DROP TABLE plant"
