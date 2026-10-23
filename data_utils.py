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
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        
        #Remove whitespace for handling
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
        
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df = df.drop_duplicates()

        df["date changed"] = pd.to_datetime(df["date changed"], errors="coerce", dayfirst=True)
        df = df[df["Date"] >= "2000-01-01"] #keep only data necessary
        
        #other column missing, avg previous and future 7 days

        return df
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
    
    return

def clean_boe(df: pd.DataFrame) -> pd.DataFrame:
    try:
        #Standardise data
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            
        #Remove whitespace for handling
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
            
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df = df.drop_duplicates()

        #ensure data is only taken after 1st jan 2000
        df["date changed"] = pd.to_datetime(df["date changed"], errors="coerce", dayfirst=True)
        df = df[df["date changed"] >= "2000-01-01"] #keep only data necessary
            
            #other column missing, avg previous and future 7 days
    
        return df
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(1)
        
    return

def clean_ons(df: pd.DataFrame) -> pd.DataFrame:
    try:
        print("n")
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit()
    return
