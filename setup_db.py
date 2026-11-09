"""
Builds the PUUMS database from the sql/ folder (drops and recreates `puums`).

    python setup_db.py                 # uses config.py
    python setup_db.py --no-seed       # schema + triggers + views + procedures only

Handles the DELIMITER blocks used by triggers/procedures, so you don't need
the mysql command-line client on PATH.
"""
import re
import sys
from pathlib import Path

import pymysql

import config

SQL_DIR = Path(__file__).parent / "sql"
FILES = ["01_schema.sql", "02_triggers.sql", "03_views.sql", "04_procedures.sql", "05_seed.sql"]


def split_statements(text):
    """Split a .sql file into statements, honouring DELIMITER changes."""
    delimiter, buf, out = ";", [], []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("DELIMITER "):
            delimiter = stripped.split()[1]
            continue
        if not buf and (stripped.startswith("--") or not stripped):
            continue
        buf.append(line)
        code = re.sub(r"\s--\s.*$", "", stripped).rstrip()     # ignore trailing comment
        if code.endswith(delimiter):
            buf[-1] = re.sub(r"\s--\s.*$", "", buf[-1]).rstrip()
            stmt = "\n".join(buf).rstrip()
            stmt = stmt[: -len(delimiter)].strip()
            if stmt:
                out.append(stmt)
            buf = []
    if "".join(buf).strip():
        out.append("\n".join(buf).strip())
    return out


def run_file(cur, path):
    count = 0
    for stmt in split_statements(path.read_text(encoding="utf-8")):
        cur.execute(stmt)
        while cur.nextset():          # drain result sets returned by CALLs
            pass
        count += 1
    print(f"  {path.name:<20} {count} statements")


def main():
    files = [f for f in FILES if not ("--no-seed" in sys.argv and f == "05_seed.sql")]
    conn = pymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
                           password=config.DB_PASSWORD, autocommit=True,
                           charset="utf8mb4", collation="utf8mb4_unicode_ci",
                           client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
    with conn.cursor() as cur:
        print("Building PUUMS database ...")
        for f in files:
            run_file(cur, SQL_DIR / f)
        cur.execute("USE puums")
        cur.execute("SELECT (SELECT COUNT(*) FROM Citizen), (SELECT COUNT(*) FROM Bill), "
                    "(SELECT COUNT(*) FROM Payment)")
        c, b, p = cur.fetchone()
        print(f"Done. {c} citizens, {b} bills, {p} payments.")
    conn.close()


if __name__ == "__main__":
    main()
