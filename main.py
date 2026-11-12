from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

from data_utils import load_data, report_missing, clean_ftse, clean_ons, clean_boe
#from sql_utils

DB_FOLDER = Path("databases")
DB_FOLDER.mkdir(parents=True, exist_ok=True)

DS_FOLDER = Path("datasets")
DS_FOLDER.mkdir(parents=True, exist_ok=True)

DB = "economic_view.db"

SCHEMA = """CREATE TABLE IF NOT EXISTS ftse100 (
                date  TEXT PRIMARY KEY,   -- ISO 'YYYY-MM-DD' so text sorts and compares correctly
                open  REAL, high REAL,
                close REAL, change REAL
            );
            CREATE TABLE IF NOT EXISTS interest_rates (
                date TEXT PRIMARY KEY,    -- date the rate changed
                rate REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cpi (
                date            TEXT PRIMARY KEY,  -- first day of the month
                cpi_annual_rate REAL NOT NULL
            );

            -- FTSE trading days with the latest known rate and CPI on or before each day
            CREATE VIEW IF NOT EXISTS v_daily AS
            SELECT f.date, f.close,
                (SELECT rate FROM interest_rates b WHERE b.date <= f.date
                ORDER BY b.date DESC LIMIT 1) AS bank_rate,
                (SELECT cpi_annual_rate FROM cpi c WHERE c.date <= f.date
                ORDER BY c.date DESC LIMIT 1) AS cpi_annual_rate
            FROM ftse100 f;
            """

"""
    ftse_df = datasets["ftse100_daily_history"]
    cpi_df = datasets["staging_ons_cpi_clean"]
    boe_df = datasets["boe_interest_rates"]
"""



def main():  
    file_paths = [
        "FTSE 100 Historical Results Price Data", #ftse100 daily data
        "mm23", #ons data
        "Bank Rate history and data  Bank of England Database" #bank of england interest rate
    ]

    name_mapping = {
        "FTSE 100 Historical Results Price Data": "ftse100",
        "mm23": "cpi",
        "Bank Rate history and data  Bank of England Database": "interest_rates"
    }

    datasets = {}

    for path in file_paths:
        #get name for file to be accessed
        raw_key = Path(path).stem

        #clean data
        clean_name = name_mapping.get(raw_key, raw_key)
        datasets[clean_name] = openData(path)

    #clean the data
    datasets["ftse100_daily_history"] = clean_ftse(datasets["ftse100"])
    datasets["boe_interest_rates"] = clean_boe(datasets["interest_rates"])
    print(datasets["boe_interest_rates"].columns.tolist())
    datasets["staging_ons_cpi_clean"] = clean_ons(datasets["cpi"])

    
      # exact header names, including any hidden characters
    print(datasets["boe_interest_rates"].head(3))
    

    report_missing(datasets["boe_interest_rates"])

    assess_data(datasets)

    #define location before creating files
    base = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base, "databases")
    os.makedirs(db_dir, exist_ok=True)
    
    
    db_path = os.path.join(db_dir, "directory.db")
    build_sql(db_path, datasets["ftse100_daily_history"], datasets["boe_interest_rates"], datasets["staging_ons_cpi_clean"])
    return


#open data, and return 
def openData(fileName):
    #check for folder, and files inside
    filePath = DS_FOLDER / f"{fileName}.csv"
    print("Opening: " + fileName)
    dataset_raw = load_data(filePath)

    #confirm dataset loads
    dataset_raw.head(1)
    #dataset = sanitise(dataset_raw)
    #report_missing(dataset)

    print(f"Opened successfully: {filePath}")
    #handle how to assess null values
    return dataset_raw

def assess_data(datasets):
    for data in datasets:
        datasets[data].info()
    return

def build_sql(db_path, ftse: pd.DataFrame, boe: pd.DataFrame, cpi: pd.DataFrame) -> None:
    ftse = ftse.copy()                                    # don't mutate the caller's frame
    ftse["date"] = pd.to_datetime(ftse["date"], dayfirst=True)  # make sure it's real datetimes (UK format)
    ftse = ftse.sort_values("date")                       # oldest first so shift(-1) means "next trading day"
    ftse["close"] = ftse["open"].shift(-1)                # next day's open stands in for today's close

    with sqlite3.connect(db_path) as con:                 # one connection, commits on success
        con.executescript(SCHEMA)                         # create tables and view if missing

        def write(table, frame, cols):
            out = frame[cols].copy()                      # keep only schema columns
            out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")  # ISO text for sqlite
            con.execute(f"DELETE FROM {table}")           # clear old rows so reruns are safe
            out.to_sql(table, con, if_exists="append", index=False)  # append keeps the primary key

        write("ftse100", ftse, ["date", "open", "high", "close"])
        write("interest_rates", boe, ["date", "rate"])
        write("cpi", cpi, ["date", "cpi_annual_rate"])
    return

def create_SQL(df: pd.DataFrame, path) -> None:
    try:
        #define location before creating files
        db_dir = os.path.join(base, "databases")
        os.makedirs(db_dir, exist_ok=True)

        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(db_dir, "directory.db")
        sql_path = os.path.join(db_dir, "directory.sql")
        if not path:
            return

        if os.path.exists(path):
            os.remove(path)
        conn = sqlite3.connect(path)
        conn.execute("""CREATE TABLE IF NOT EXISTS ftse100 (
                date  TEXT PRIMARY KEY,   -- ISO 'YYYY-MM-DD' so text sorts and compares correctly
                open  REAL, high REAL,
                close REAL, change REAL
            );
            CREATE TABLE IF NOT EXISTS interest_rates (
                date TEXT PRIMARY KEY,    -- date the rate changed
                rate REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cpi (
                date            TEXT PRIMARY KEY,  -- first day of the month
                cpi_annual_rate REAL NOT NULL
            );

            -- FTSE trading days with the latest known rate and CPI on or before each day
            CREATE VIEW IF NOT EXISTS v_daily AS
            SELECT f.date, f.close,
                (SELECT rate FROM interest_rates b WHERE b.date <= f.date
                ORDER BY b.date DESC LIMIT 1) AS bank_rate,
                (SELECT cpi_annual_rate FROM cpi c WHERE c.date <= f.date
                ORDER BY c.date DESC LIMIT 1) AS cpi_annual_rate
            FROM ftse100 f;
            """)

    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)

#output sql data to a text file
def analytics_handler():
    #ask user for use: report, sql file, .vb file
    print("Select an option: Report, vb file, none")
    #check folder

    #open folder

    #basics

    #sql write
    print("hello world")
    return



if __name__ == "__main__":
    main()