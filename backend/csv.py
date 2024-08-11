### Importing data from CSV into accounts

# TODO move to test file
import codecs
import csv
from datetime import date, datetime
from typing import BinaryIO, Dict, List
from sqlalchemy import Enum
from sqlalchemy.orm import Session

from database.models import Account, Transaction


class Headers(Enum):
    # Essential fields
    POST_DATE = "post_date"
    DESCRIPTION = "description"
    AMOUNT = "amount"

    # Less essential/hints
    INIT_DATE = "init_date"
    TYPE = "type"
    CATEGORY = "category"
    BALANCE = "balance"


header_aliases: Dict[str, Headers] = {
    "transaction date": Headers.INIT_DATE,
    "posting date": Headers.POST_DATE,
    "post date": Headers.POST_DATE,
    "description": Headers.DESCRIPTION,
    "description": Headers.DESCRIPTION,
    "amount": Headers.AMOUNT,
    "type": Headers.TYPE,
    "balance": Headers.BALANCE,
    "category": Headers.CATEGORY,
}

HeaderMapping = Dict[Headers, int]


class ConflictingHeaderException(Exception):
    pass


def add_transactions(
    session: Session, account: Account | None, records: List[Transaction]
):
    with session.begin() as transaction:
        for record in records:
            record.account = account
            session.add(record)
        transaction.commit()


def parse_header_line(keys: List[str]) -> HeaderMapping:
    headers = {}
    for idx, key in enumerate(keys):
        header_key = header_aliases.get(key.lower())
        if header_key in headers:
            conflicting_key = keys[headers[header_key]]
            raise ConflictingHeaderException(
                f"Conflicting headers: {key} and {conflicting_key} both map to {header_key}"
            )
        elif header_key:
            headers[header_key] = idx
        else:
            print(f"Ignoring unrecognized header: {key}")
    return headers


def _parse_date(date_string: str) -> date:
    format = "%m/%d/%Y"
    parsed_datetime = datetime.strptime(date_string, format)
    return parsed_datetime.date()


def parse_transaction(headers: HeaderMapping, line: List[str]):
    new_record = Transaction(
        post_date=_parse_date(line[headers[Headers.POST_DATE]]),
        description=line[headers[Headers.DESCRIPTION]],
        amount=line[headers[Headers.AMOUNT]],
    )

    # Parse optional fields if present
    if Headers.INIT_DATE in headers:
        new_record.init_date = _parse_date(line[headers[Headers.INIT_DATE]])

    return new_record


def parse_csv(file: BinaryIO) -> List[Transaction]:
    headers: HeaderMapping | None = None
    transactions: List[Transaction] = []
    textFile = codecs.getreader("utf-8")(file)
    csv_reader = csv.reader(textFile, delimiter=",", quotechar='"')
    for line_number, line in enumerate(csv_reader):
        if line_number == 0:
            headers = parse_header_line(line)
        elif len(line) < 1:
            print(f"Unexpected empty line in CSV at line {line_number}")
        else:
            transactions.append(parse_transaction(headers, line))
    return transactions
