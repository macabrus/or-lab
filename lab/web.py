from attr import fields
from flask import Flask, jsonify, request
from flask_cors import CORS

from lab.db import make_conn
from lab.models import Plant
from lab.utils import decode_query_object

app = Flask(__name__)
if not app.debug:  # enable cors when serving from dev server in nodejs
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
    return {f.name for f in fields(model)}


def make_order_clause(order_obj):
    order_by = []
    props = field_names(Plant)
    for col in order_obj:
        prop, direction = col["prop"], col["direction"]
        if prop not in props:
            continue
        order_by.append(f"{prop} {direction.upper()}")
    return ", ".join(order_by)


@app.route("/api/plant")
def get_plants():
    args = request.args
    filter_by = args.get("filter", {"*": None}, type=decode_query_object)
    order_by = args.get(
        "order",
        [{"prop": "id", "direction": "desc"}],
        type=decode_query_object,
    )
    page_size = args.get("size", 5, type=int)
    page = args.get("page", 0, type=int)

    where, where_params = make_where_clause(filter_by)
    where = where or "true"

    order = make_order_clause(order_by)

    sql = f"""
        select * from plant
        where {where}
        order by {order}
        limit ?
        offset ?
    """
    params = (*where_params, page_size, page * page_size)
    print(sql)
    print(params)

    with make_conn("test.db") as db:
        return jsonify(db.execute(sql, params).fetchall())
