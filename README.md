# zerto-operation
##

# prerequisite
python -m venv .venv
<br>pip install -r requirements.txt

# execute zerto_usage.py
.venv\Scripts\activate
<br>python .\zerto_usage.py -m 5 <may zip files>

## usage
usage: zerto_usage.py [-h] [-m MONTH] [-y YEAR] zip_files [zip_files ...]

positional arguments:
  zip_files          List of Zerto zip files to process separated by space.

options:
  -h, --help         show this help message and exit
  -m, --month MONTH  Indicate the month number (1 to 12) to process.
  -y, --year YEAR    Indicate the year number (2025) to process.
