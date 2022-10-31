import csv, json, sqlite3, attr

from contextlib import closing
from attr import fields
from cattrs import unstructure
from lab.models import Genus, Plant
from lab.utils import Table, Relation, reduce_rows, columns, alias_map
from lab.db import make_conn

def import_data():
    plant_prop_map = {"name": "species"}
    genus_prop_map = {"name": "genus"}
    plant_prop_ignore = ("id",)
    genus_prop_ignore = ("id", "species")
    plant_id = ("name",)
    genus_id = ("name",)
    model_rows = []

    # load csv into models
    with open("biljke.csv", newline="") as f:
        reader = csv.DictReader(f, delimiter=",", quotechar="'", skipinitialspace=True)
        for row in reader:
            plant_dict = {}
            for prop in fields(Plant):
                if prop.name in plant_prop_ignore:
                    continue
                csv_prop = plant_prop_map.get(prop.name, prop.name)
                plant_dict[prop.name] = prop.type(row[csv_prop])
            print(Plant(**plant_dict))
            genus_dict = {}
            for prop in fields(Genus):
                if prop.name in genus_prop_ignore:
                    continue
                csv_prop = genus_prop_map.get(prop.name, prop.name)
                genus_dict[prop.name] = prop.type(row[csv_prop])
            print(Genus(**genus_dict))
            model_rows.append({Genus: Genus(**genus_dict), Plant: Plant(**plant_dict)})

    # insert models into database, track relations
    id_map = {}  # model => id
    with sqlite3.connect("test.db") as connection:
        with closing(connection.cursor()) as cur:
            for row in model_rows:
                genus, plant = row[Genus], row[Plant]
                if genus.name not in id_map:
                    cur.execute(
                        f"""
                        INSERT INTO genus({csv_props(Genus, exclude={'id', 'species'})})
                        VALUES ({csv_placeholders(Genus, exclude={'id', 'species'})})
                        """,
                        astuple(genus, exclude={"id", "species"}),
                    )
                    id_map[genus.name] = cur.lastrowid
                cur.execute(
                    f"""
                    INSERT INTO plant(genus_id, {csv_props(Plant, exclude={'id'})})
                    VALUES (?, {csv_placeholders(Plant, exclude={'id'})})
                    """,
                    (id_map[genus.name], *astuple(plant, exclude={"id"})),
                )
                id_map[plant.name] = cur.lastrowid
        # check insertions
        with closing(connection.cursor()) as cur:
            cur.execute(f"select {csv_props(Genus, exclude={'species'})} from genus")
            for row in cur.fetchall():
                print(row)
            cur.execute(f"select {csv_props(Plant)} from plant")
            for row in cur.fetchall():
                print(row)
        print("Done.")


def csv_props(model, exclude=set()):
    return ", ".join(f.name for f in fields(model) if f.name not in exclude)


def csv_placeholders(model, exclude=set()):
    return ", ".join("?" for f in fields(model) if f.name not in exclude)


def astuple(model, exclude=set()):
    return tuple(
        getattr(model, prop.name)
        for prop in fields(type(model))
        if prop.name not in exclude
    )


def export_data():
    print("exporting data")
    with make_conn('test.db') as connection:
        with closing(connection.cursor()) as cur:
            cur.execute(f'''
                SELECT {columns(Genus, table='g', alias=alias_map('g', Genus), skip={'species'})},
                       {columns(Plant, table='p', alias=alias_map('p', Plant))}
                FROM genus AS g
                LEFT JOIN plant AS p
                ON g.id = p.genus_id
            ''')
            rows = cur.fetchall()
            plant_table = Table(prefix='p', row_model=Plant, primary_key='id')
            genus_table = Table(prefix='g', row_model=Genus, primary_key='id')
            relations = [
                Relation(parent=genus_table, child=plant_table, ref_prop='species')
            ]
            denormalised = reduce_rows(rows, *relations)[Genus]
            print(json.dumps(unstructure(denormalised), default=str, indent=4))

