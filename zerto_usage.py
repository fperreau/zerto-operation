import pandas as pd
from datetime import datetime as dt
import argparse as ap
import regex as re
import os
from zipfile import ZipFile

billing_file = "ZertoBilling.zip"
date_format = "%m/%d/%Y%H:%M:%S%p"
out = pd.DataFrame(columns=["file", "max", "count"]+["d"+str(i+1) for i in range(0,31)])

def browse_csv_file(file, zip_file, days, count):
    """
    Reads a CSV file containing Zerto billing data and processes it to find the maximum number of days with recorded usage.

    Parameters:
    file (str): Name of the CSV file to read.
    zip_file (str): Name of the ZIP file containing the CSV file.
    days (list): List of 31 integers where the index is the day of the month and the value is the count of days with usage.
    count (int): The total count of days with recorded usage.

    Returns:
    tuple: days and count
    """
    df = pd.read_csv(file, skiprows=1, usecols=[" VM (Unique ID)", " From Date", " To Date", " Total Days"])
    df.rename(columns={' VM (Unique ID)': 'VM_Unique_ID'}, inplace=True)
    df.rename(columns={' From Date': 'From_Date'}, inplace=True)
    df.rename(columns={' To Date': 'To_Date'}, inplace=True)
    df.rename(columns={' Total Days': 'Total_Days'}, inplace=True)
 
    csv_days = [0]*31
    csv_count = 0

    for row in df.itertuples():
        dFrom = dt.strptime(re.sub('[ ?]','',row.From_Date),date_format)
        dTo = dt.strptime(re.sub('[ ?]','',row.To_Date),date_format)
        for d in range(dFrom.day,dTo.day+1):
            days[d-1] += 1
            csv_days[d-1] += 1
        csv_count += 1
    count += csv_count

    out.loc[len(out)] = dict({"file": zip_file, "max": max(csv_days), "count": csv_count},
                             **{"d"+str(index+1): element for index,element in enumerate(csv_days)})

    return (days,count)

def browse_zip_file(zip_file,csv_file,days,count):
    """
    Extracts and processes a CSV file from a ZIP file containing Zerto billing data.

    Parameters:
    zip_file (str): The path to the main ZIP file containing the billing ZIP file.
    csv_file (str): The name of the CSV file inside the billing ZIP file to be processed.
    days (list): A list of 31 integers representing the days of the month with usage counts.
    count (int): The total count of days with recorded usage.

    Returns:
    tuple: Updated days and count after processing the CSV file.
    """
    try:
        with ZipFile(zip_file,'r') as zip:
            zip.extract(billing_file)
            with ZipFile(billing_file,'r') as bill:
                with bill.open(csv_file) as file:
                    (days,count)=browse_csv_file(file,zip_file,days,count)
    
    except Exception as e:
        print(f"Error extract {billing_file} or {csv_file} from {zip_file} : {e}")

    return (days,count)

def find_max_days(zip_files,csv_file,year,month):
    """
    Processes a list of Zerto ZIP files to determine the maximum number of days
    with recorded usage within a specified month and year.

    Parameters:
    zip_files (list): A list of ZIP file paths to process.
    csv_file (str): The name of the CSV file to extract and read from each ZIP file.
    year (int): The year to process.
    month (int): The month to process.

    Returns:
    None
    """
    days = [0] * 31
    max_days = []
    count = 0

    for zip_file in zip_files:
        (days,count) = browse_zip_file(zip_file,csv_file,days,count)
    os.remove(billing_file)

    max_day = max(days)
    for d in range(1,31+1):
        if days[d-1] == max_day: max_days.append("d"+str(d))

    out.loc[len(out)] = dict({"file": "TOTAL", "max": max_day, "count": count},
                             **{"d"+str(index+1): element for index,element in enumerate(days)})

    print(f"{out}\n\nZerto usage for {month}-{year} ==> {max_day} {max_days}/{count}\n")
    out.to_csv(f"{year}{month:02d}_Resiliency_France.csv",sep=';', encoding='utf-8',index=False, header=True)

def main():
    """
    Main function to process a list of Zerto ZIP files to determine the maximum number of days with recorded usage within a specified month and year.

    Parameters:
    None

    Returns:
    None
    """
    today = dt.now()
    parser = ap.ArgumentParser()
    parser.add_argument('-m', '--month', type=int, default=today.month - 1, help='Indicate the month number (1 to 12) to process.')
    parser.add_argument('-y', '--year', type=int, default=today.year, help='Indicate the year number (2025) to process.')
    parser.add_argument('zip_files', nargs='+', help='List of Zerto zip files to process separated by space.')
    args = parser.parse_args()

    find_max_days(args.zip_files, f"ZertoBilling_{args.month}_{args.year}.csv", args.year, args.month)

if __name__ == "__main__":
    main()