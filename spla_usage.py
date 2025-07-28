import pandas as pd
from datetime import datetime as dt
import argparse as ap
import regex as re
import os
from zipfile import ZipFile

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

def browse_vminfo():
    sr=pd.DataFrame(columns=["Model", "Manufacturer", "tProcessor", "Processor"])
    sr.loc[len(sr)]=dict({"Model": "7X06-CTO1WW SR650", "Manufacturer": "Lenovo", "tProcessor": "Intel", "Processor": "Xeon"})

    hw=pd.read_excel("./vInfoTool/20250728_1042_HDC-Impact.xlsx",sheet_name="ESX")
    hw.rename(columns={'Type / Model': 'Model'}, inplace=True)
    hw.rename(columns={'Warranty \nStart': 'iDate'}, inplace=True)

    df=pd.read_excel("./vInfoTool/20250203_0806_ypb000vcnt11.bcrs.fr_report.xlsx",sheet_name="vmInfo")
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
                "date": hw.loc[hw['Hostname'] == row.vmhost.split('.')[0]].iDate.values[0].strftime("%Y-%m-%d"),
                "host": row.vmhost  
            })
            
    print(out.sort_values(by=['host','vmName']))

def main():
    today = dt.now()
    parser = ap.ArgumentParser()
    args = parser.parse_args()
    browse_vminfo()

if __name__ == "__main__":
    main()