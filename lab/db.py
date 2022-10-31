import sqlite3


def init_schema():
    with sqlite3.connect("test.db") as db:
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


def drop_schema():
    with sqlite3.connect("test.db") as db:
        db.execute("DROP TABLE genus")
        db.execute("DROP TABLE plant")
