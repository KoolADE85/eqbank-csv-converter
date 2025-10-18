import os
import sys
from operator import itemgetter

csv_file = [argv for argv in sys.argv if argv.endswith(".csv")]
if csv_file:
    # Get just the filename, not the full path
    filename = os.path.basename(csv_file[0])
    account_num = filename.split(" ")[0]
else:
    account_num = ""
assert account_num.isnumeric(), "Could not detect account number from csv file name."


mapping = {
    "has_header": True,
    "bank": "EQ Bank",
    "currency": "CAD",
    "delimiter": ",",
    "account": account_num,
    "account_id": account_num,
    "date": itemgetter("Transfer date"),
    "date_fmt": "%Y-%m-%d",
    "payee": itemgetter("Description"),
    "type": lambda tr: "DEBIT" if tr.get("Amount", "").startswith("-") else "CREDIT",
    "amount": lambda tr: tr.get("Amount"),
    "balance": itemgetter("Balance"),
}
