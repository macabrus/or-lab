import codecs
import json
from base64 import b64decode, b64encode
from typing import Any, Callable, get_origin
from urllib.parse import quote, unquote

import attrs
from attrs import define, field, fields


@define(kw_only=True, hash=True)
class Table:
    prefix: str
    row_model: Any  # model representing row in database
    primary_key: str
    mapper: Callable = field(default=lambda o: o, hash=False)


# relation representation for resutset rows
# TODO: implement usage in reduce_rows() method
@define(kw_only=True)
class Relation:
    parent: Table
    child: Table
    ref_prop: str


def reduce_rows(rows, *relations: Relation):
    # related entities
    tables: set[Table] = set()
    for rel in relations:
        tables.add(rel.parent)
        tables.add(rel.child)
    # reverse lookup id maps
    id_maps: dict[Any, dict] = {}
    # properties per entity
    entity_props = {}
    for table in tables:
        if table.row_model not in entity_props:
            print(table)
            cls = table.row_model
            props = fields(cls)
            entity_props[cls] = tuple(prop.name for prop in props)
            id_maps[cls] = {}
    for row in rows:
        row_entities = {}
        # make dictionaries from subsets of columns
        for table in tables:

            id_col = table.prefix + "_" + table.primary_key
            # skip null entities for left/right joins
            if row[id_col] is None:
                row_entities[table.row_model] = None
                continue
            id_map = id_maps[table.row_model]
            if row[id_col] not in id_map:
                subset_dict = {}
                for k, v in row.items():
                    if k.startswith(table.prefix + "_"):
                        subset_dict[k[len(table.prefix) + 1 :]] = v
                # construct attrs class instances for every object
                # print(subset_dict)
                entity = table.row_model(**subset_dict)
                id_map[row[id_col]] = entity
            row_entities[table.row_model] = id_map[row[id_col]]
        # set up relations between objects specified by relations
        for rel in relations:
            parent_entity = row_entities[rel.parent.row_model]
            child_entity = row_entities[rel.child.row_model]
            if parent_entity is None or child_entity is None:
                continue
            parent_id = getattr(parent_entity, rel.parent.primary_key)
            child_id = getattr(child_entity, rel.child.primary_key)
            # in case of null left/right joins,
            # dont make relations with all null tables
            if parent_id is None or child_id is None:
                continue
            ref_prop = rel.ref_prop
            # get type hint for relation holder
            # check if it is set, list or primitive
            rel_type = next(
                get_origin(field.type)
                for field in fields(type(parent_entity))
                if field.name == rel.ref_prop
            )
            # print(rel_type)
            if rel_type is list:  # append to it
                getattr(parent_entity, ref_prop).append(child_entity)
            elif rel_type is set:  # add to it if not already in
                getattr(parent_entity, ref_prop).add(child_entity)
            else:  # just set prop
                setattr(parent_entity, ref_prop, child_entity)
    return {k: list(v.values()) for k, v in id_maps.items()}


def alias_map(prefix: str, cls: Any):
    props = [prop.name for prop in fields(cls)]
    return {prop: f"{prefix}_{prop}" for prop in props}


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def columns(
    obj, skip=[], table=None, prefix=None, placeholders=False, alias={}
):
    props = []
    if isinstance(obj, dict):
        props = obj.values()
    elif attrs.has(obj):
        props = [prop.name for prop in fields(obj)]
    else:
        raise ValueError("Unknown type")
    props = filter(lambda prop: prop not in skip, props)
    if not placeholders:
        if prefix:
            alias = alias_map(prefix, obj)
        props = map(lambda p: f"{p} as {alias[p]}" if p in alias else p, props)
    if table:
        props = map(lambda prop: f"{table}.{prop}", props)
    if placeholders:
        props = [f":{prop}" for prop in props]
    return ", ".join(props)


def csv_props(model, skip=set()):
    return ", ".join(f.name for f in fields(model) if f.name not in skip)


def csv_placeholders(model, skip=set()):
    return ", ".join("?" for f in fields(model) if f.name not in skip)


def astuple(model, skip=set()):
    return tuple(
        getattr(model, prop.name)
        for prop in fields(type(model))
        if prop.name not in skip
    )


def encode_query_object(obj: dict):
    str_obj = json.dumps(obj, sort_keys=True)
    zipped_str = codecs.encode(str_obj.encode("utf8"), "zlib")
    b64_str = b64encode(zipped_str).decode("utf8")
    url_enc = quote(b64_str)
    return url_enc


def decode_query_object(text: str):
    if text is None:
        return text
    url_decoded = unquote(text)
    b64_decoded = b64decode(url_decoded)
    unzipped = codecs.decode(b64_decoded, "zlib")
    str_decoded = unzipped.decode("utf8")
    return json.loads(str_decoded)
