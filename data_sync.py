"""
BOILERPLATE: Fetch data from one source table (with optional WHERE / subqueries)
and batch-insert into a target table.

Copy this file, rename it, then fill in CONFIG and adjust the query logic below.
- Simple case: one table, one equality WHERE (use WHERE_COLUMN / WHERE_VALUE).
- Complex case: subqueries / IN (...) — reflect extra tables and build stmt below.

Expects SOURCE_DB_URL and TARGET_DB_URL in environment (e.g. from .env in script dir).
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, MetaData, Table, Column, and_, text
)
from sqlalchemy.sql import select

# Load .env from this script's directory (or set SOURCE_DB_URL / TARGET_DB_URL in env)
load_dotenv(Path(__file__).resolve().parent / ".env")

# =====================================================
# CONFIG — fill in your values
# =====================================================

SOURCE_DB_URL = os.environ["SOURCE_DB_URL"]
TARGET_DB_URL = os.environ["TARGET_DB_URL"]

# Schema/owner on source DB (e.g. "MYSCHEMA"). Use None if no schema.
SOURCE_OWNER = "MYSCHEMA"

# Name of the table on the TARGET DB (will be created if missing).
TABLE_NAME = "target_table_name"

# Name of the table or view on the SOURCE DB that you are selecting FROM.
SOURCE_TABLE_NAME = "source_table_or_view_name"

# How many rows to insert per batch (e.g. 1000, 2000, 5000).
BATCH_SIZE = 2000

# Optional row limit for testing. Set to None for full run; set to e.g. 100 to test.
ROW_LIMIT = None

# If True, drop the target table before creating (ORA-00942 ignored if table missing).
DROP_TARGET_IF_EXISTS = False

# --- Simple WHERE (single column = value). Ignore if you use subqueries below. ---
WHERE_COLUMN = "status"
WHERE_VALUE = "ACTIVE"

# =====================================================
# ENGINE & METADATA — no need to change
# =====================================================

source_engine = create_engine(SOURCE_DB_URL)
target_engine = create_engine(TARGET_DB_URL)

source_metadata = MetaData()
target_metadata = MetaData()

# =====================================================
# DATA FETCH & INSERT
# =====================================================

def migrate_data():
    source_conn = source_engine.connect()

    # ---------------------------------------------
    # 1) Reflect the main source table/view
    #    Replace SOURCE_TABLE_NAME / SOURCE_OWNER with your source object.
    # ---------------------------------------------
    reflect_kw = {"autoload_with": source_engine}
    if SOURCE_OWNER:
        reflect_kw["schema"] = SOURCE_OWNER
    source_table = Table(SOURCE_TABLE_NAME, source_metadata, **reflect_kw)

    # ---------------------------------------------
    # 2) Optional: reflect extra tables for subqueries
    #    Only needed if your WHERE uses IN (subquery). Add one Table() per table.
    # ---------------------------------------------
    # extra_table_a = Table(
    #     "other_table_a",
    #     source_metadata,
    #     schema=SOURCE_OWNER,
    #     autoload_with=source_engine
    # )
    # extra_table_b = Table(
    #     "other_table_b",
    #     source_metadata,
    #     schema=SOURCE_OWNER,
    #     autoload_with=source_engine
    # )

    # ---------------------------------------------
    # 3) Create target table from source columns
    #    TABLE_NAME is used here; columns are copied from source_table.
    # ---------------------------------------------
    target_table = Table(
        TABLE_NAME,
        target_metadata,
        *[
            Column(
                col.name,
                col.type,
                primary_key=col.primary_key,
                nullable=col.nullable
            )
            for col in source_table.columns
        ]
    )
    pk_cols = [c.name for c in target_table.primary_key.columns]
    print(f"Target table: {TABLE_NAME} | PK columns: {pk_cols or '(none)'} | Columns: {len(target_table.columns)}")

    if DROP_TARGET_IF_EXISTS:
        try:
            with target_engine.begin() as conn:
                conn.execute(text(f"DROP TABLE {TABLE_NAME}"))
        except Exception as e:
            if "942" not in str(e) and "00942" not in str(e):
                raise
        print(f"Dropped (if existed) and creating target table {TABLE_NAME}")

    target_metadata.create_all(target_engine)

    # ---------------------------------------------
    # 4) Build the SELECT and WHERE
    #
    # Option A — Simple: one column = one value
    #   stmt = select(...).where(source_table.c[WHERE_COLUMN] == WHERE_VALUE)
    #
    # Option B — With subqueries (e.g. main_col IN (SELECT ... FROM other_table))
    #   subq = select(extra_table_a.c.some_col).where(...)
    #   stmt = select(...).where(source_table.c.main_col.in_(subq))
    #
    # Add .limit(ROW_LIMIT) only when ROW_LIMIT is not None (done below).
    # ---------------------------------------------
    stmt = select(
        *[source_table.c[col.name] for col in target_table.columns]
    ).where(
        source_table.c[WHERE_COLUMN] == WHERE_VALUE
    )

    # Optional: use a subquery instead of simple equality, e.g.:
    # subq = select(extra_table_a.c.id).where(extra_table_a.c.flag == "Y")
    # stmt = select(...).where(source_table.c.fk_id.in_(subq))

    if ROW_LIMIT is not None:
        stmt = stmt.limit(ROW_LIMIT)

    result = source_conn.execute(stmt)
    all_rows = result.mappings().all()

    limit_msg = f", limit={ROW_LIMIT}" if ROW_LIMIT else ""
    print(f"Fetched {len(all_rows)} rows from source DB (batch_size={BATCH_SIZE}{limit_msg})")

    total = 0
    rows = []
    batch_num = 0

    # ---------------------------------------------
    # 5) Batch insert into target
    # ---------------------------------------------
    with target_engine.begin() as target_conn:
        for row in all_rows:
            rows.append(
                {col.name: row[col.name] for col in target_table.columns}
            )
            if len(rows) >= BATCH_SIZE:
                target_conn.execute(target_table.insert(), rows)
                total += len(rows)
                batch_num += 1
                print(f"  Batch {batch_num}: inserted {len(rows)} rows (total: {total})")
                rows.clear()

        if rows:
            target_conn.execute(target_table.insert(), rows)
            total += len(rows)
            batch_num += 1
            print(f"  Batch {batch_num}: inserted {len(rows)} rows (total: {total})")

    source_conn.close()
    print(f"Done. Rows inserted: {total}")

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    print(f"Starting fetch: {SOURCE_TABLE_NAME} -> {TABLE_NAME}...")
    migrate_data()
    print("Done")
