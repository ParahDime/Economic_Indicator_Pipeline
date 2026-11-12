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
                open  REAL, high REAL, low REAL, 
                close REAL
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
    #each name mapped for easier reading
    for path in file_paths:
        #get name for file to be accessed
        raw_key = Path(path).stem

        #clean data
        clean_name = name_mapping.get(raw_key, raw_key)
        datasets[clean_name] = openData(path)

    #data is cleaned and assigned a variable
    datasets["ftse100_daily_history"] = clean_ftse(datasets["ftse100"])
    datasets["boe_interest_rates"] = clean_boe(datasets["interest_rates"])
    datasets["staging_ons_cpi_clean"] = clean_ons(datasets["cpi"])
    
    report_missing(datasets["boe_interest_rates"])

    assess_data(datasets)

    #define location before creating files
    base = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base, "databases")
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, "directory.db")
    build_sql(db_path, datasets["ftse100_daily_history"], datasets["boe_interest_rates"], datasets["staging_ons_cpi_clean"])
    
    report = assess_db(db_path)
    return


#soft check if file can be found
def openData(fileName):
    #check for folder, and files inside
    filePath = DS_FOLDER / f"{fileName}.csv"
    print("Opening: " + fileName)
    dataset_raw = load_data(filePath)

    #confirm dataset loads
    dataset_raw.head(1)

    print(f"Opened successfully: {filePath}")
    #handle how to assess null values
    return dataset_raw

def assess_data(datasets):
    for data in datasets:
        datasets[data].info()
    return

#construct the database as a .db file
def build_sql(db_path, ftse: pd.DataFrame, boe: pd.DataFrame, cpi: pd.DataFrame) -> None:
    ftse = ftse.copy()
    ftse["date"] = pd.to_datetime(ftse["date"], dayfirst=True)
    ftse = ftse.sort_values("date") #go by oldest first
    ftse["close"] = ftse["open"].shift(-1) #define closing value

    #ensure values are strings for reading and manipulating data
    price_cols = ["open", "high", "low", "close"]
    for col in price_cols:
        ftse[col] = pd.to_numeric(ftse[col].astype(str).str.replace(",", ""), errors="coerce")

    #construct the .db file
    with sqlite3.connect(db_path) as con:
        con.executescript(SCHEMA)

        def write(table, frame, cols):
            out = frame[cols].copy()
            out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")  #ISO text for sqlite
            con.execute(f"DELETE FROM {table}")
            out.to_sql(table, con, if_exists="append", index=False)

        #write to each table of the database, corresponding to each dataset
        write("ftse100", ftse, ["date", "open", "high", "low", "close"])
        write("interest_rates", boe, ["date", "rate"])
        write("cpi", cpi, ["date", "cpi_annual_rate"])
    return

#output sql data to a text file
def assess_db(db_path) -> pd.DataFrame:
    results = []  # collects (check, status, detail) rows

    def add(check, ok, detail="", level="FAIL"):
        # ok -> "OK", otherwise the severity passed in (FAIL or WARN)
        results.append((check, "OK" if ok else level, detail))

    with sqlite3.connect(db_path) as con:
        q = lambda sql: pd.read_sql(sql, con)  # shorthand for running a query

        # --- per-table basics: row count, date range ---
        for t in ["ftse100", "interest_rates", "cpi"]:
            r = q(f"SELECT COUNT(*) n, MIN(date) lo, MAX(date) hi FROM {t}").iloc[0]
            add(f"{t}: has rows", r.n > 0, f"{r.n} rows, {r.lo} to {r.hi}")

        # --- FTSE checks ---
        f = q("SELECT * FROM ftse100 ORDER BY date")
        f["date"] = pd.to_datetime(f["date"])

        nulls = f[["open", "high", "low"]].isna().sum().sum()
        add("ftse: no null open/high/low", nulls == 0, f"{nulls} nulls")

        n_close = f["close"].isna().sum()
        add("ftse: only last close is null", n_close <= 1, f"{n_close} null closes", "WARN")

        bad_hl = (f["high"] < f["low"]).sum()
        add("ftse: high >= low", bad_hl == 0, f"{bad_hl} rows violate")

        print(f.dtypes)                      # open should be float64, not object
        print(f["open"].head())

        moves = f["open"].pct_change().abs()  # day-to-day change in open
        big = (moves > 0.10).sum()
        add("ftse: no >10% daily moves", big == 0, f"{big} large moves (check for parse errors)", "WARN")

        gaps = f["date"].diff().dt.days.gt(5).sum()  # >5 days = more than a weekend + bank holiday
        add("ftse: no gaps >5 days", gaps == 0, f"{gaps} gaps", "WARN")

        age = (pd.Timestamp.today().normalize() - f["date"].max()).days
        add("ftse: data is fresh", age <= 5, f"latest is {age} days old", "WARN")

        # --- BoE checks ---
        b = q("SELECT * FROM interest_rates")
        add("boe: rate in 0-20%", b["rate"].between(0, 20).all(),
            f"min {b['rate'].min()}, max {b['rate'].max()}")

        # --- CPI checks ---
        c = q("SELECT * FROM cpi ORDER BY date")
        c["date"] = pd.to_datetime(c["date"])
        expected = pd.date_range(c["date"].min(), c["date"].max(), freq="MS")  # every month start
        missing = len(expected) - len(c)
        add("cpi: no missing months", missing == 0, f"{missing} months missing", "WARN")

        # --- joined view: do the as-of lookups find a value? ---
        v = q("SELECT * FROM v_daily")
        for col in ["bank_rate", "cpi_annual_rate"]:
            n = v[col].isna().sum()
            add(f"view: {col} filled on every day", n == 0, f"{n} null days", "WARN")

    report = pd.DataFrame(results, columns=["check", "status", "detail"])
    print(report.to_string(index=False))                        # readable summary
    print("\n", report["status"].value_counts().to_dict())      # e.g. {'OK': 12, 'WARN': 2}
    return report 



if __name__ == "__main__":
    main()