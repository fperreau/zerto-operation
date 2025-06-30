# zerto-operation
##

# prerequisite
python -m venv .venv
pip install -r requirements.txt

# execute zerto_usage.py
.venv\Scripts\activate
python .\zerto_usage.py -m 5 202505_Phoenix_UsageReport.zip BRSERM_MOP_202505.zip BRSK24_MOP_202505.zip Cegid_report_May2025.zip
p