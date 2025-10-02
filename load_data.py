import pandas as pd
import sqlite3

# --- Configuration ---
EXCEL_FILE = 'AI-Analyst-Data-Set.xlsx'
DB_FILE = 'retail_analysis.db'

# List of sheets to load. Make sure these names exactly match your Excel sheet tabs.
SHEET_NAMES = ['Orders', 'Cancels', 'Inventory', 'Store', 'Product', 'Calendar']

print(f"Starting data loading process from '{EXCEL_FILE}'...")

try:
    # 1. Read all sheets from the Excel file into a dictionary of DataFrames
    all_data = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAMES)
    print("Successfully read all sheets from Excel.")
    
    # 2. Connect to the SQLite database. It will be created if it doesn't exist.
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Connected to database '{DB_FILE}'.")
    
    # 3. Iterate through each sheet and load the data into a corresponding SQL table
    for sheet_name in SHEET_NAMES:
        df = all_data[sheet_name]
        
        # Use a case-insensitive string replacement to fix any potential space/formatting issues
        # in column names for SQL compatibility (e.g., 'Item ID' -> 'Item_ID')
        df.columns = [col.replace(' ', '_').replace('.', '').replace('-', '') for col in df.columns]

        # Use 'replace' to ensure a clean load (drops table and recreates it each time)
        df.to_sql(sheet_name, conn, if_exists='replace', index=False)
        print(f"    - Loaded sheet '{sheet_name}' into table '{sheet_name}'. ({len(df):,} rows)")
        
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("\nData loading complete. Database is ready for analysis!")

except FileNotFoundError:
    print(f"\nERROR: The file '{EXCEL_FILE}' was not found.")
    print("Please ensure the Excel workbook is in the same directory and correctly named.")
except Exception as e:
    print(f"\nAn error occurred during the loading process: {e}")