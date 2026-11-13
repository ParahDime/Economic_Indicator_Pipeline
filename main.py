from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

from data_utils import load_data, report_missing, clean_ftse, clean_ons, clean_boe
from sql_utils import build_sql, assess_db

DB_FOLDER = Path("databases")
DB_FOLDER.mkdir(parents=True, exist_ok=True)

DS_FOLDER = Path("datasets")
DS_FOLDER.mkdir(parents=True, exist_ok=True)

DB = "economic_view.db"



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

    #move stuff to sql_utils.py
    db_path = os.path.join(db_dir, "directory.db")
    build_sql(db_path, datasets["ftse100_daily_history"], datasets["boe_interest_rates"], datasets["staging_ons_cpi_clean"])
    
    report = assess_db(db_path)

    #function for creating image matplotlib
    
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




if __name__ == "__main__":
    main()