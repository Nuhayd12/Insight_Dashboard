# Only to check the schema of the tables so that we can check for wrong names or typos

import sqlite3
import pandas as pd

DB_FILE = 'retail_analysis.db'
conn = sqlite3.connect(DB_FILE)

# Fetch and print schema info for the most critical tables
tables_to_check = ['Orders', 'Cancels', 'Calendar', 'Store', 'Product']

print("--- Database Schema Check ---")
for table_name in tables_to_check:
    print(f"\nSchema for table: {table_name}")
    # PRAGMA table_info is the standard SQLite way to inspect a table's schema
    schema_df = pd.read_sql(f"PRAGMA table_info({table_name});", conn)
    # The 'name' column shows the actual, final column names
    print(schema_df[['name']].to_string(index=False))

conn.close()