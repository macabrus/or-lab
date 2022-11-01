import argparse
import csv
import json
import os
import sqlite3
from contextlib import closing

import attr
from attr import fields
from cattrs import structure, unstructure

from lab.db import drop_schema, init_schema, make_conn, open_txn
from lab.models import Genus, Plant
from lab.utils import (Relation, Table, alias_map, astuple, columns,
                       csv_placeholders, csv_props, reduce_rows)


def load_csv(args) -> list[Genus]:
    plant_prop_map = {"name": "species"}
    genus_prop_map = {"name": "genus"}
    plant_prop_ignore = ("id",)
    genus_prop_ignore = ("id", "species")
    plant_id = ("name",)
    genus_id = ("name",)
    model_rows = []

    # load csv into models
    with open(args.file, newline="") as f:
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
    return model_rows


def load_json(args):
    with open(args.file, "r") as f:
        data = structure(json.load(f), list[Genus])
    model_rows = []
    for genus in data:
        for plant in genus.species:
            model_rows.append({Genus: genus, Plant: plant})
    return model_rows


def import_data(args):
    if args.file.endswith(".csv"):
        model_rows = load_csv(args)
    elif args.file.endswith(".json"):
        model_rows = load_json(args)

    # insert models into database, track relations
    with make_conn(args.database) as db, open_txn(db):
        id_map = {}  # entity => id
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


def export_sql(args):
    with make_conn(args.database) as db, open(args.file, "w") as f:
        for line in db.iterdump():
            f.write(line + os.linesep)


def export_csv(args, data):
    inv_genus_map = {v: k for k, v in alias_map("g", Genus).items()}
    inv_plant_map = {v: k for k, v in alias_map("p", Plant).items()}
    renames = inv_genus_map | inv_plant_map | {"g_name": "genus", "p_name": "species"}

    csv_fields = {f.name for f in fields(Genus)}
    csv_fields |= {f.name for f in fields(Plant)}
    csv_fields |= {'species', 'genus'}
    csv_fields -= {"id", 'name'}

    with open(args.file, "w") as f:
        writer = csv.DictWriter(
            f, csv_fields, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL
        )
        writer.writeheader()
        for row in data:
            row = {renames[k]: v for k, v in row.items() if renames[k] in csv_fields}
            writer.writerow(row)


def export_json(args, data):
    table_plant = Table(prefix="p", row_model=Plant, primary_key="id")
    table_genus = Table(prefix="g", row_model=Genus, primary_key="id")
    relations = (Relation(parent=table_genus, child=table_plant, ref_prop="species"),)
    denormalised = reduce_rows(data, *relations)[Genus]
    with open(args.file, "w") as f:
        f.write(json.dumps(unstructure(denormalised), indent=4))


def export_data(args):
    if os.path.isfile(args.file):
        print(f"File '{args.file}' already exists. Skipping.")
        return
    if args.file.endswith(".sql"):
        export_sql(args)
        return

    with make_conn(args.database) as db, open_txn(db):
        rows = db.execute(
            f"""
            SELECT {columns(Genus, table='g', alias=alias_map('g', Genus), skip={'species'})},
                   {columns(Plant, table='p', alias=alias_map('p', Plant))}
            FROM genus AS g
            LEFT JOIN plant AS p
            ON g.id = p.genus_id
        """
        ).fetchall()

    if args.file.endswith(".json"):
        export_json(args, rows)
    elif args.file.endswith(".csv"):
        export_csv(args, rows)


def start():
    parser = argparse.ArgumentParser(description="Alat za otvoreno računarstvo")
    subparsers = parser.add_subparsers(dest="command")

    schema_parser = subparsers.add_parser("schema")
    schema_parser.add_argument(
        "--database", "-d", type=str, default="test.db", help="(default: %(default)s)"
    )
    schema_parser.add_argument("action", choices=["init", "drop"])

    data_parser = subparsers.add_parser("data")
    data_parser.add_argument(
        "--database", "-d", type=str, default="test.db", help="(default: %(default)s)"
    )
    data_parser.add_argument(
        "--file", "-f", type=str, default="biljke.csv", help="(default: %(default)s)"
    )
    data_parser.add_argument("action", choices=["import", "export"])

    args = parser.parse_args()

    if "schema" == args.command:
        if "init" == args.action:
            init_schema(args)
        elif "drop" == args.action:
            drop_schema(args)
    elif "data" == args.command:
        if "import" == args.action:
            import_data(args)
        elif "export" == args.action:
            export_data(args)
