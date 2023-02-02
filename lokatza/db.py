"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""

import os

import sqlite3
from contextlib import closing

DB = os.path.join('.db',' lokatza.db')

class Database(object):
    '''
    Database manager
    '''

    def __init__(self):
        self._connection = sqlite3.connect(DB)
        self._init_db()

    def _init_db(self):
        with closing(self._connection.cursor()) as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS players
                (id INTEGER NOT NULL PRIMARY KEY,
                name TEXT,
                phone TEXT,
                cyclists TEXT NOT NULL)""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS baselines
                (id INTEGER NOT NULL PRIMARY KEY,
                baseline TEXT NOT NULL)""")

    def add_player(self, id, name, phone, cyclists):
        query = "INSERT INTO players VALUES (?, ?, ?, ?)  ON CONFLICT(id) DO UPDATE SET name=excluded.name, phone=excluded.phone, cyclists=excluded.cyclists"
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(query, (str(id), name, phone, cyclists))
        self._connection.commit()

    def get_players(self):
        query = "SELECT id, name, phone, cyclists FROM players"
        with closing(self._connection.cursor()) as cursor:
            return cursor.execute(query).fetchall()

    def delete_players(self):
        query = "DELETE FROM players"
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(query)

    def add_baseline(self, id, baseline):
        query = "INSERT INTO baselines VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET baseline=excluded.baseline"
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(query, (str(id), baseline))
        self._connection.commit()

    def get_baseline(self, id):
        query = "SELECT id, baseline FROM baselines WHERE id = ?"
        with closing(self._connection.cursor()) as cursor:
            return cursor.execute(query, (str(id),)).fetchone()

    def get_baselines(self):
        query = "SELECT id, baseline FROM baselines"
        with closing(self._connection.cursor()) as cursor:
            return cursor.execute(query).fetchall()

    def close(self):
        self._connection.close()