import sqlite3
from contextlib import contextmanager

from lab.sql import CREATE_GENUS, CREATE_PLANT, DROP_GENUS, DROP_PLANT
from lab.utils import dict_factory


def init_schema(args):
    with make_conn(args.database) as db, open_txn(db):
        db.execute(CREATE_GENUS)
        db.execute(CREATE_PLANT)


def drop_schema(args):
    with make_conn(args.database) as db, open_txn(db):
        db.execute(DROP_GENUS)
        db.execute(DROP_PLANT)


@contextmanager
def make_conn(url: str):
    try:
        con = sqlite3.connect(
            url,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        con.row_factory = dict_factory
        yield con
    finally:
        con.close()


@contextmanager
def open_txn(db):
    try:
        # db.cursor()
        db.execute("BEGIN")
        yield
        db.execute("COMMIT")
    except Exception as e:
        db.execute("ROLLBACK")
        raise e
