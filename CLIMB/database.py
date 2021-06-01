import sqlite3
from os import path

from flask import g


class Database:
    """ Provides connection to database. """

    def __init__(self, app=None):
        self.app = app
        self.database_name = 'DATABASE.sqlite3'
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """ Adds teardown and initialises database if needed. """

        self.app = app
        database_name = app.config['DATABASE_NAME']
        if database_name:
            self.database_name = database_name
        app.teardown_appcontext(self.teardown)
        if not path.isfile(self.database_name):
            self.init_db()

    def connect(self):
        """ Returns a connection to database. """

        db = sqlite3.connect(self.database_name)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        return db

    def teardown(self, exception):
        """ Closes an open connection to database. """

        db = g.pop('db', None)
        if db is not None:
            db.close()

    @property
    def connection(self):
        """ Adds connection to request context. """

        if 'db' not in g:
            g.db = self.connect()
        return g.db

    def init_db(self):
        """ Initialise the database from schema. """

        conn = self.connect()
        with self.app.open_resource('schema.sql') as f:
            conn.executescript(f.read().decode('utf8'))

        conn.executescript("""
        INSERT INTO setting (name, value) VALUES ('FIRST_RUN', '1');
        
        INSERT INTO permission (name) VALUES ('MEMBER_DATA');
        INSERT INTO permission (name) VALUES ('STAFF_DATA');
        INSERT INTO permission (name) VALUES ('BOOKINGS');
        INSERT INTO permission (name) VALUES ('VIEW_TRANSACTIONS');
        INSERT INTO permission (name) VALUES ('MAKE_TRANSACTIONS');
        INSERT INTO permission (name) VALUES ('SETTINGS');
        INSERT INTO permission (name) VALUES ('STORE_CONFIG');
        
        INSERT INTO weekly_opening_days (day, open) values ('monday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('tuesday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('wednesday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('thursday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('friday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('saturday', 0);
        INSERT INTO weekly_opening_days (day, open) values ('sunday', 0);
        """)
