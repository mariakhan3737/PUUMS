"""Thin database layer. Every statement the GUI runs is sent to the SQL log
panel, so during the demo you can show the exact query behind each screen."""
import datetime
import re
import sys
from pathlib import Path

import pymysql

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

_listeners = []


def on_sql(callback):
    """Register a function(str) that receives every executed SQL statement."""
    _listeners.append(callback)


def _emit(text):
    stamp = datetime.datetime.now().strftime("%H:%M:%S")
    one_line = re.sub(r"\s+", " ", text).strip()
    for cb in _listeners:
        cb(f"-- {stamp}\n{one_line};\n")


class DBError(Exception):
    """Raised with the MySQL message (trigger / constraint text) for the UI."""


class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
            password=config.DB_PASSWORD, database=config.DB_NAME,
            charset="utf8mb4", collation="utf8mb4_unicode_ci", autocommit=True)

    def _run(self, cur, sql, params=None):
        text = cur.mogrify(sql, params) if params is not None else sql
        _emit(text)
        try:
            cur.execute(sql, params)
        except pymysql.MySQLError as e:
            _emit(f"-- ERROR: {e.args[1] if len(e.args) > 1 else e}")
            raise DBError(e.args[1] if len(e.args) > 1 else str(e)) from e

    def query(self, sql, params=None):
        """SELECT -> (column_names, rows)."""
        with self.conn.cursor() as cur:
            self._run(cur, sql, params)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            while cur.nextset():
                pass
            return cols, list(rows)

    def one(self, sql, params=None):
        _, rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=None):
        """INSERT/UPDATE/DELETE -> lastrowid."""
        with self.conn.cursor() as cur:
            self._run(cur, sql, params)
            while cur.nextset():
                pass
            return cur.lastrowid

    def call(self, sql, params=None, out_vars=()):
        """CALL a procedure. Returns (result_rows, out_values)."""
        with self.conn.cursor() as cur:
            self._run(cur, sql, params)
            rows = []
            while True:
                if cur.description:
                    rows.extend(cur.fetchall())
                if not cur.nextset():
                    break
        out = ()
        if out_vars:
            out = self.one("SELECT " + ", ".join(out_vars))
        return rows, out

    def transaction(self, statements):
        """Run [(sql, params), ...] atomically from Python (START/COMMIT/ROLLBACK)."""
        with self.conn.cursor() as cur:
            self._run(cur, "START TRANSACTION")
            try:
                ids = []
                for sql, params in statements:
                    self._run(cur, sql, params)
                    ids.append(cur.lastrowid)
                self._run(cur, "COMMIT")
                return ids
            except DBError:
                self._run(cur, "ROLLBACK")
                raise
