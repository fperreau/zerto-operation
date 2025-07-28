import pandas as pd
from datetime import datetime as dt
import argparse as ap
import regex as re
import os
from zipfile import ZipFile

HDC_IMPACT = "20250728_1042_HDC-Impact.xlsx"

out = pd.DataFrame(
    columns=[
        "vmName",
        "product",
        "shared",
        "version",
        "edition",
        "pType",
        "pModel",
        "cpu",
        "nbUser",
        "purpose",
        "license",
        "date",
        "host"
    ]
)

def browse_vminfo(file):
    global HDC_IMPACT

    sr=pd.DataFrame(columns=["Model", "Manufacturer", "tProcessor", "Processor"])
    sr.loc[len(sr)]=dict({"Model": "7X06-CTO1WW SR650", "Manufacturer": "Lenovo", "tProcessor": "Intel", "Processor": "Xeon"})

    hw=pd.read_excel(HDC_IMPACT,sheet_name="ESX")
    hw.rename(columns={'Type / Model': 'Model'}, inplace=True)
    hw.rename(columns={'Warranty \nStart': 'iDate'}, inplace=True)

    df=pd.read_excel(file,sheet_name="vmInfo")
    for row in df.itertuples():
        if row.VM[0] == "w":
            model=hw.loc[hw['Hostname'] == row.vmhost.split('.')[0]].Model.values[0].strip()

            out.loc[len(out)] = dict({
                "vmName": row.VM,
                "product": "Windows Server",
                "shared": True,
                "version": row.vmOS,
                "edition": "standard",
                "pType": sr.loc[sr['Model'] == model].tProcessor.values[0],
                "pModel": sr.loc[sr['Model'] == model].Processor.values[0],
                "cpu": row.Cpu,
                "nbUser": "5",
                "purpose": row.VM[6:10],
                "license": "spla",
                "date": hw.loc[hw['Hostname'] == row.vmhost.split('.')[0]].iDate.values[0],
                "host": row.vmhost  
            })
            
def browse_vminfo_list(vminfo_file):
    for file in vminfo_file:
        browse_vminfo(file)
#    print(out.sort_values(by=['host','vmName']))
    print(out)
    
def main():
    today = dt.now()
    parser = ap.ArgumentParser()
    parser.add_argument('vminfo_file', nargs='+', help='VMInfo files to process separated by space.')
    args = parser.parse_args()
    browse_vminfo_list(args.vminfo_file)

if __name__ == "__main__":
    main()