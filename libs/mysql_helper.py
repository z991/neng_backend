# __author__ = itsneo1990
import logging

import pymysql


class Connection(object):
    def __init__(self, host, database, user=None, password=None, port=3306):
        self.host = host
        self.port = port
        self.database = database

        args = dict(use_unicode=True, charset="utf8", host=host, database=database, port=int(port),
                    db=database, init_command='SET time_zone = "+8:00"',
                    sql_mode="TRADITIONAL")
        if user:
            args["user"] = user
        if password:
            args["password"] = password
        self._db = None
        self._db_args = args
        try:
            self.reconnect()
        except pymysql.Error:
            logging.error("Cannot connect to MySQL on %s", self.host, exc_info=True)

    def close(self):
        """Closes this database connection."""
        if self._db is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = pymysql.Connection(**self._db_args)
        self._db.autocommit(False)

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [ObjDict(zip(column_names, row)) for row in cursor]
        finally:
            cursor.close()

    def _cursor(self):
        if self._db is None:
            self.reconnect()
        try:
            self._db.ping()
        except pymysql.MySQLError:
            self.reconnect()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters):
        try:
            return cursor.execute(query, parameters)
        except pymysql.OperationalError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.close()
            raise

    def __del__(self):
        self.close()

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.
        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()


class ObjDict(dict):
    """A dict that allows for object-like property access syntax."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return "0"

    def __setattr__(self, key, value):
        self[key] = value
