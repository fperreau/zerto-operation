import pandas as pd
from datetime import datetime as dt
import argparse as ap
import regex as re
import os
from zipfile import ZipFile

billing_file = "ZertoBilling.zip"
date_format = "%m/%d/%Y%H:%M:%S%p"

row = ["file", "max", "count"] + ["d"+str(i+1) for i in range(0,31)]
out = pd.DataFrame(columns=row)

def browse_csv_file(file, zip_file, days, max, count):
    """
    Reads a CSV file containing Zerto billing data and processes it to find the maximum number of days with recorded usage.

    Parameters:
    file (file): The file to read.
    zip_file (str): The name of the ZIP file containing the CSV file.
    days (list): List of 33 integers where the index is the day of the month and the value is the count of days with usage.
    max (int): The maximum number of days with recorded usage.
    count (int): The total count of VMs.

    Returns:
    tuple: days, max, and count
    """
    csv_days = [0]*31
    csv_max = -1

    df = pd.read_csv(file, skiprows=1, usecols=[" VM (Unique ID)", " From Date", " To Date", " Total Days"])
    df.rename(columns={' VM (Unique ID)': 'VM_Unique_ID'}, inplace=True)
    df.rename(columns={' From Date': 'From_Date'}, inplace=True)
    df.rename(columns={' To Date': 'To_Date'}, inplace=True)
    df.rename(columns={' Total Days': 'Total_Days'}, inplace=True)
 
    csv_count = 0
    for row in df.itertuples():
        dFrom = dt.strptime(re.sub('[ ?]','',row.From_Date),date_format)
        dTo = dt.strptime(re.sub('[ ?]','',row.To_Date),date_format)

        #print(dFrom.day,dTo.day,row.Total_Days,list(range(dFrom.day,dTo.day+1)))
        for d in range(dFrom.day,dTo.day+1):
            days[d-1] += 1
            csv_days[d-1] += 1

        csv_count += 1

    for d in range(1,31+1):
        if csv_days[d-1] > csv_max: csv_max = csv_days[d-1]

    count += csv_count

    row = {"file": zip_file, "max": csv_max, "count": csv_count}
    row.update({"d"+str(index+1): element for index,element in enumerate(csv_days)})
    out.loc[len(out)] = row

    return (days,max,count)

def browse_zip_file(zip_file,csv_file,days,max,count):
    """
    Reads a ZIP file containing Zerto billing data and processes it to find the maximum number of days with recorded usage.

    Parameters:
    zip_file (str): Name of the ZIP file to read.
    csv_file (str): Name of the CSV file to read in the ZIP file.
    days (list): List of 33 integers where the index is the day of the month and the value is the count of days with usage.
    max (int): The maximum number of days with recorded usage.

    Returns:
    tuple: days and max
    """
    try:
        with ZipFile(zip_file,'r') as zip:
            zip.extract(billing_file)
            with ZipFile(billing_file,'r') as bill:
                with bill.open(csv_file) as file:
                    (days,max,count)=browse_csv_file(file,zip_file,days,max,count)
    
    except Exception as e:
        print(f"Error extract {billing_file} or {csv_file} from {zip_file} : {e}")

    return (days,max,count)

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
    max=-1
    max_day = []
    count = 0
    title = "################### Zerto CSV file"
    total = "TOTAL"

    for zip_file in zip_files:
        (days,max,count) = browse_zip_file(zip_file,csv_file,days,max,count)

    for d in range(1,31+1):
        if days[d-1] > max: max = days[d-1]

    for d in range(1,31+1):
        if days[d-1] == max: max_day.append(d)

    os.remove(billing_file)

    row = {"file": "TOTAL", "max": max, "count": count}
    row2 = {"d"+str(index+1): element for index,element in enumerate(days)}
    row.update(row2)
    out.loc[len(out)] = row

    #pd.options.display.max_colwidth = 200
    print(f"{out}\n\nZerto usage for {month}-{year} ==> {max} {max_day}/{count}\n")

def main():
    """
    Processes Zerto billing data in ZIP files to find the maximum number of days with recorded usage.

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