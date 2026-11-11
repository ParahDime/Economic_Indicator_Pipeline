import pandas as pd
from pathlib import Path
import sys

#load dataset
def load_data(path: str) -> pd.DataFrame:
    try:    
        ext = Path(path).suffix.lower()

        if ext == ".csv":
            return pd.read_csv(path)
        elif ext in (".xlsx", ".xls"):
            return pd.read_excel(path)
        elif ext == ".json":
            return pd.read_json(path)
        else:
            #error handle if not found
            errorMsg = ValueError(f"Unsupported file type: {ext}")
            print(ValueError)
            sys.exit()
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)

def report_missing(df: pd.DataFrame) -> pd.Series:
    #view nulls by column
    return df.isna().sum().sort_values(ascending=False)
    return

def clean_ftse(df: pd.DataFrame) -> pd.DataFrame:
    try:
        #Standardise data
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        
        #Remove whitespace for handling
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
        
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df = df.drop_duplicates()

        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
        df = df[df["date"] >= "2000-01-01"] #keep only data necessary
        
        #other column missing, avg previous and future 7 days

        return df
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
    
    return

def clean_boe(df: pd.DataFrame) -> pd.DataFrame:
    try:
        #Standardise data
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
            
        #Remove whitespace for handling
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
            
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df = df.drop_duplicates()

        #ensure data is only taken after 1st jan 2000
        df["date"] = pd.to_datetime(df["date_changed"], errors="coerce", dayfirst=True)
        df = df[df["date"] >= "2000-01-01"] #keep only data necessary
        df = df.drop(columns=["date_changed"], errors="ignore")
            #other column missing, avg previous and future 7 days
    
        return df
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
        
    return

def clean_ons(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df.rename(columns={df.columns[0]: "period"})
        #remove all rows < 2000
        #keep row CPI ANNUAL RATE 00: ALL ITEMS 2015=100
        codes = df[df["period"] == "CDID"].iloc[0]  # the metadata row listing each series code
        col = codes[codes == "D7G7"].index[0]

        df = df[["period", col]]
        df.columns = ["period", "cpi_annual_rate"]

        df = df[df["period"].str.match(r"^\d{4} [A-Z]{3}$", na=False)].copy()

        df["date"] = pd.to_datetime(df["period"], format="%Y %b")  # "2024 JAN" -> 2024-01-01
        df["cpi_annual_rate"] = pd.to_numeric(df["cpi_annual_rate"], errors="coerce")
        return df.drop(columns="period").dropna()
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit()
    return
