import os
import sys
from operator import itemgetter

csv_file = [argv for argv in sys.argv if argv.endswith(".csv")]
if csv_file:
    filename = os.path.basename(csv_file[0])
    account_num = filename.split(" ")[0]
else:
    account_num = ""
assert account_num.isnumeric(), "Could not detect account number from csv file name."


def get_type(tr: dict[str, str]):
    return "DEBIT" if tr.get("Amount", "").startswith("-") else "CREDIT"


def get_amount(tr: dict[str, str]):
    return tr.get("Amount")


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
    "type": get_type,
    "amount": get_amount,
    "balance": itemgetter("Balance"),
}
