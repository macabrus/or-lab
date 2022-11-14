import json
from csv import DictWriter
from io import StringIO

from attr import define, fields
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS

from lab.db import make_conn, open_txn
from lab.models import Plant
from lab.utils import decode_query_object

app = Flask(__name__)
# enable cors when serving from dev server in nodejs
CORS(app, origins=["http://localhost:3000"])


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
            for i, row in enumerate(cur.execute(sql, params), start=1):
                sep = ","
                if i == cur.rowcount:
                    sep = ""
                yield json.dumps(row) + sep
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
        return jsonify(db.execute(sql, params).fetchall())
