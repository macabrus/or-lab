import json
import os
from csv import DictWriter
from io import StringIO

from attr import define, fields
from cattrs import structure, unstructure
from flask import (
    Flask,
    Response,
    request,
    send_from_directory,
    stream_with_context,
)
from flask_cors import CORS

from lab.db import make_conn, open_txn
from lab.models import CreatePlant, Plant, UpdatePlant
from lab.sql import INSERT_PLANT_SQL
from lab.utils import astuple, decode_query_object

app = Flask(__name__)
# enable cors when serving from dev server in nodejs
CORS(app, origins=["http://localhost:3000", "http://localhost:8000"])


def make_where_clause(filter_obj):
    where = []
    params = []
    for prop in field_names(Plant):
        if filter_obj.get(prop, None):
            where.append(f"LOWER({prop}) LIKE LOWER(?)")
            params.append(f"%{filter_obj[prop]}%")
        elif filter_obj.get("*", None):
            where.append(f"LOWER({prop}) LIKE LOWER(?)")
            params.append(f"%{filter_obj['*']}%")
    return " OR ".join(where), params


def make_set_clause(patch_obj):
    print("Patch obj", patch_obj)
    updated_fields = []
    for f in fields(UpdatePlant):
        value = getattr(patch_obj, f.name, None)
        if value is None:
            continue
        updated_fields.append(f.name)
    print(updated_fields)
    available_fields = field_names(Plant)
    clause = []
    params = []
    for f in updated_fields:
        if f not in available_fields:
            continue
        clause.append(f"{f} = ?")
        params.append(getattr(patch_obj, f))
    print(available_fields)
    return ", ".join(clause), params


def field_names(model):
    return [f.name for f in fields(model)]


def make_order_clause(order_obj):
    order_by = []
    props = field_names(Plant)
    for col in order_obj:
        prop, direction = col["prop"], col["direction"]
        if prop not in props:
            continue
        order_by.append(f"{prop} {direction.upper()}")
    return ", ".join(order_by)


@app.get("/api/schema/plant")
def get_schema():
    return list(field_names(Plant))


@app.get("/download/<format>")
def download_as_file(format):
    if format not in {"json", "csv"}:
        return 400, "Unsupported format"

    args = parse_filter_args(request.args)
    sql, params = get_filter_sql(args)

    def stream_json():
        with make_conn("test.db") as db, open_txn(db) as cur:
            yield "["
            cur.execute(sql, params)
            rows = cur.fetchmany()
            print(len(rows))
            while True:
                if not rows:
                    break
                yield ",".join(map(json.dumps, rows))
                tmp_rows = cur.fetchmany()
                if tmp_rows:
                    yield ","
                    rows = tmp_rows
                else:
                    break
            yield "]"

    def stream_csv():
        stream = StringIO()
        writer = DictWriter(stream, fieldnames=field_names(Plant))
        writer.writeheader()
        with make_conn("test.db") as db, open_txn(db) as cur:
            for i, row in enumerate(cur.execute(sql, params), start=1):
                row.pop("genus_id")
                writer.writerow(row)
                yield stream.getvalue().replace("\x00", "")
                stream.truncate(0)

    format_generators = {"json": stream_json, "csv": stream_csv}
    headers = {"Content-Disposition": f"attachment;filename=biljke.{format}"}
    mime_types = {"json": "application/json", "csv": "text/csv"}

    return Response(
        stream_with_context(format_generators[format]()),
        mimetype=mime_types[format],
        headers=headers,
    )


@define
class FilterArgs:
    filter_by: dict
    order_by: dict
    page_size: int
    page: int


def parse_filter_args(args) -> FilterArgs:
    args = request.args
    filter_by = args.get("filter", {"*": None}, type=decode_query_object)
    order_by = args.get(
        "order",
        [{"prop": "id", "direction": "desc"}],
        type=decode_query_object,
    )
    page_size = args.get("size", 5, type=int)
    page = args.get("page", 0, type=int)
    return FilterArgs(
        filter_by=filter_by,
        order_by=order_by,
        page_size=page_size,
        page=page,
    )


def get_filter_sql(args: FilterArgs):
    where, where_params = make_where_clause(args.filter_by)
    where = where or "true"

    order = make_order_clause(args.order_by)

    sql = f"""
        select * from plant
        where {where}
        order by {order}
        limit ?
        offset ?
    """
    params = (*where_params, args.page_size, args.page * args.page_size)
    return sql, params


@app.get("/api/plant")
def get_plants():
    args = parse_filter_args(request.args)
    sql, params = get_filter_sql(args)
    print(sql)
    print(params)

    with make_conn("test.db") as db:
        return db.execute(sql, params).fetchall(), 200


@app.get("/api/plant/<int:id>")
def get_plant(id):
    sql = "select * from plant where rowid = ?"
    with make_conn("test.db") as db:
        row = db.execute(sql, (id,)).fetchone()
    if not row:
        return {
            "status": 404,
            "message": "Plant not found",
            "detail": None,
        }, 404
    return row, 200


@app.post("/api/plant")
def add_plant():
    new_plant = structure(request.json, CreatePlant)
    print(new_plant)
    with make_conn("test.db") as db, open_txn(db) as db:
        db.execute(
            INSERT_PLANT_SQL,
            astuple(new_plant, skip={"id"}),
        )
    return {
        "status": 201,
        "message": "Plant added successfully",
        "detail": unstructure(new_plant),
    }, 201


@app.delete("/api/plant/<int:id>")
def remove_plant(id):
    with make_conn("test.db") as db:
        row = db.execute(
            "delete from plant where id = ? returning *", (id,)
        ).fetchone()
    if not row:
        return {
            "status": 404,
            "message": "Plant not found",
            "details": None,
        }, 404
    return {"status": 200, "message": "Removed plant", "details": row}, 200


@app.patch("/api/plant/<int:id>")
def update_plant(id):
    update_dto = structure(request.json, UpdatePlant)
    clause, params = make_set_clause(update_dto)
    print(clause, params)
    if not params:
        return {
            "status": 400,
            "message": "Expected fields to update",
            "details": None,
        }, 400
    with make_conn("test.db") as db, open_txn(db) as db:
        row = db.execute(
            f"update plant set {clause} where id = ? returning *",
            (*params, id),
        ).fetchone()
    return row, 200


@app.get("/docs")
def serve_swagger():
    base = os.path.join(os.path.dirname(__file__), "assets")
    return send_from_directory(base, "swagger/index.html")
