import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, registry

from backend.csv import add_transactions, parse_csv
from database.models import Account, Base, Transaction


@pytest.fixture
def session():
    # echo=True for debugging
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)


def test_models(session: Session):
    test_user = Account(name="Ryan")
    session.add(test_user)
    session.commit()

    found_user = session.query(Account).filter(Account.name == "Ryan").first()
    assert found_user.id == test_user.id


def test_import_checking_csv(session: Session):
    account = Account(name="checking_account")
    session.add(account)
    session.commit()

    path = "./test_data/sensitive/sample_transactions_checking.CSV"
    with open(path) as file:
        records = parse_csv(file)
        add_transactions(session, account, records)

    assert session.query(Transaction).count() == 19


def test_import_credit_csv(session: Session):
    account = Account(name="credit_account")
    session.add(account)
    session.commit()

    path = "./test_data/sensitive/sample_transactions_credit.CSV"
    with open(path) as file:
        records = parse_csv(file)
        add_transactions(session, account, records)

    assert session.query(Transaction).count() == 20
