# db.py
# This file connects to MySQL and runs all our queries.
# Every screen uses these functions instead of talking to MySQL directly.

import pymysql
from app import config

# the SQL log box at the bottom of the window registers itself here,
# so every query we run can be shown on the screen
log_function = None


def on_sql(function):
    global log_function
    log_function = function


def show_in_log(text):
    print(text)
    if log_function is not None:
        log_function(text + ";\n")


# our own error, the screens catch this and show the message in a popup
class DBError(Exception):
    pass


class Database:

    def __init__(self):
        # open the connection to MySQL using the details in config.py
        self.conn = pymysql.connect(host=config.DB_HOST,
                                    port=config.DB_PORT,
                                    user=config.DB_USER,
                                    password=config.DB_PASSWORD,
                                    database=config.DB_NAME,
                                    charset="utf8mb4",
                                    collation="utf8mb4_unicode_ci",
                                    autocommit=True)

    def run(self, cursor, sql, params=None):
        # show the query (with the real values filled in) in the log
        show_in_log(cursor.mogrify(sql, params))
        try:
            cursor.execute(sql, params)
        except pymysql.MySQLError as e:
            # e.args[1] is the message from MySQL, for example from a trigger
            message = str(e.args[1])
            show_in_log("ERROR: " + message)
            raise DBError(message)

    # SELECT -> returns column names and rows
    def query(self, sql, params=None):
        cursor = self.conn.cursor()
        self.run(cursor, sql, params)
        rows = cursor.fetchall()
        columns = []
        for col in cursor.description:
            columns.append(col[0])
        cursor.close()
        return columns, list(rows)

    # SELECT that should return only one row
    def one(self, sql, params=None):
        columns, rows = self.query(sql, params)
        if len(rows) == 0:
            return None
        return rows[0]

    # INSERT / UPDATE / DELETE
    def execute(self, sql, params=None):
        cursor = self.conn.cursor()
        self.run(cursor, sql, params)
        new_id = cursor.lastrowid
        cursor.close()
        return new_id

    # CALL a stored procedure
    # out_vars are the @variables the procedure fills, e.g. ("@pid", "@msg")
    def call(self, sql, params=None, out_vars=()):
        cursor = self.conn.cursor()
        self.run(cursor, sql, params)
        rows = []
        # a procedure can send back more than one result, so read all of them
        while True:
            if cursor.description is not None:
                rows = rows + list(cursor.fetchall())
            if not cursor.nextset():
                break
        cursor.close()

        out_values = ()
        if len(out_vars) > 0:
            out_values = self.one("SELECT " + ", ".join(out_vars))
        return rows, out_values

    # run many statements together: either all of them are saved or none
    def transaction(self, statements):
        cursor = self.conn.cursor()
        self.run(cursor, "START TRANSACTION")
        try:
            for sql, params in statements:
                self.run(cursor, sql, params)
            self.run(cursor, "COMMIT")
        except DBError:
            self.run(cursor, "ROLLBACK")
            cursor.close()
            raise
        cursor.close()
