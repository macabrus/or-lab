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
