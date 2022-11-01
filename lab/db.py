import sqlite3
from contextlib import contextmanager

from lab.utils import dict_factory


def init_schema(args):
    with make_conn(args.database) as db, open_txn(db):
        db.execute(
            """
        CREATE TABLE genus(
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
        """
        )
        db.execute(
            """
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
        )
        """
        )


def drop_schema(args):
    with make_conn(args.database) as db, open_txn(db):
        db.execute("DROP TABLE genus")
        db.execute("DROP TABLE plant")


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
