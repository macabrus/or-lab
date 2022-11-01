import csv, json, sqlite3, attr

from contextlib import closing
from attr import fields
from cattrs import unstructure
from lab.models import Genus, Plant
from lab.utils import (
    Table,
    Relation,
    reduce_rows,
    columns,
    alias_map,
    csv_props,
    csv_placeholders,
    astuple,
)
from lab.db import make_conn, open_txn


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
    with make_conn("test.db") as db, open_txn(db):
        id_map = {}  # model => id
        for row in model_rows:
            genus, plant = row[Genus], row[Plant]
            if genus.name not in id_map:
                res = db.execute(
                    f"""
                    INSERT INTO genus({csv_props(Genus, skip={'id', 'species'})})
                    VALUES ({csv_placeholders(Genus, skip={'id', 'species'})})
                    """,
                    astuple(genus, skip={"id", "species"}),
                )
                id_map[genus.name] = res.lastrowid
            res = db.execute(
                f"""
                INSERT INTO plant(genus_id, {csv_props(Plant, skip={'id'})})
                VALUES (?, {csv_placeholders(Plant, skip={'id'})})
                """,
                (id_map[genus.name], *astuple(plant, skip={"id"})),
            )
            id_map[plant.name] = res.lastrowid
        # check insertions
        res = db.execute(f"select {csv_props(Genus, skip={'species'})} from genus")
        for row in res.fetchall():
            print(row)
        res = db.execute(f"select {csv_props(Plant)} from plant")
        for row in res.fetchall():
            print(row)
    print("Done.")


def export_data():
    print("exporting data")
    with make_conn("test.db") as db, open_txn(db):
        rows = db.execute(
            f"""
            SELECT {columns(Genus, table='g', alias=alias_map('g', Genus), skip={'species'})},
                   {columns(Plant, table='p', alias=alias_map('p', Plant))}
            FROM genus AS g
            LEFT JOIN plant AS p
            ON g.id = p.genus_id
        """
        ).fetchall()
        plant_table = Table(prefix="p", row_model=Plant, primary_key="id")
        genus_table = Table(prefix="g", row_model=Genus, primary_key="id")
        relations = [
            Relation(parent=genus_table, child=plant_table, ref_prop="species")
        ]
        denormalised = reduce_rows(rows, *relations)[Genus]
        print(json.dumps(unstructure(denormalised), default=str, indent=4))
