from pathlib import Path
import sqlite3
import pandas as pd


from data_utils import load_data, sanitise, report_missing
#from sql_utils

DB_FOLDER = Path("databases")
DB_FOLDER.mkdir(parents=True, exist_ok=True)


#main function
def main():
    #open ftse100 dataset

    #open interest rate data

    #open ons data




    print("hello world")
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


#output sql data to a text file
def analytics_report():
    #check folder

    #open folder

    #basics

    #sql write
    print("hello world")
    return

main()