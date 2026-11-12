# Economic Indicator

## Overview:
Data pipeline written in python to take in multiple datasets, cleans data and outputs into a .db file available for use with other systems. Data is also checked for any anomoly values, checking for null values or any other potential anomalies. 


## How to use:
The program requires the use of datasets in order to be run.

Reports can be obtained at the following
FTSE100 Daily data: https://uk.investing.com/indices/uk-100
Bank of england interest rates:https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp under export, excel
Consumer price index data: https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceindices

Once the datasets have been downloaded, they will need to be placed in the root of this program, in a folder called datasets.

Reports, such as a .db file will be created and stored in a datasets folder. This folder will be created if it does not yet exist.

### Data flow
Data is input into the program via functions, with the data then cleaned. This includes renaming columns for data for better readability, removing unwanted columns and removing data outside of the data range.

Data is then normalised, and ingested into a database. Date is used as a primary key, available on all 3 datasets. Data is then read by the program, outputting both to a variable as a plug-in for other programs, in addition to the console itself to display anomolies with a warning level dependant on the about of anomalies. 

