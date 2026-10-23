from pathlib import Path
import sqlite3
import pandas as pd


from data_utils import load_data, sanitise, report_missing, clean_ftse, clean_ons, clean_boe
#from sql_utils

DB_FOLDER = Path("databases")
DB_FOLDER.mkdir(parents=True, exist_ok=True)



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
        datasets[clean_name] = load_data(path)

    #clean the data
    """ Check and verify call"""
    datasets["ftse100_daily_history"] = clean_ftse(datasets["ftse100_daily_history"])
    datasets["staging_ons_cpi_clean"] = clean_ons(datasets["staging_ons_cpi_clean"])
    datasets["boe_interest_rates"] = clean_boe(datasets["boe_interest_rates"])

    assess_data(datasets)
    return

#open data, and return 
def openData(fileName):
    #check for folder, and files inside
    filePath = fileName + ".csv"
    print("Opening: " + fileName)
    dataset_raw = load_data(filePath)

    #confirm dataset loads
    dataset_raw.head(1)
    dataset = sanitise(dataset_raw)
    report_missing(dataset)

    print(f"Opened successfully: {filePath}")
    #handle how to assess null values
    return

def assess_data(datasets):
    for data in datasets:
        datasets[data].info()
        
    return

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

main()