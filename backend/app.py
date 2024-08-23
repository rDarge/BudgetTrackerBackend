import os
from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import uvicorn

from backend.csv import parse_csv
from backend.messages import (
    AccountData,
    CategoryData,
    GetCategoriesResponse,
    GetTransactionsResponse,
    PostAccountRequest,
    PostCategoryRequest,
    SupercategoryData,
    TransactionData,
    UpdateTransactionRequest,
    UpdateTransactionResponse,
)
from database.models import (
    Account,
    Category,
    Rule,
    Supercategory,
    Transaction,
    TransactionFile,
)

app = FastAPI()

origins = ["http://localhost:8000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Alive"}


default_engine = None


def get_default_engine():
    if default_engine:
        return default_engine
    conn_string = os.environ.get("SQLALCHEMY_CONNECTION_STRING")
    engine = create_engine(conn_string, future=True)
    return Session(engine)


async def session():
    return get_default_engine()


SessionDep = Annotated[Session, Depends(session)]


@app.post("/account", response_model=AccountData)
async def post_account(session: SessionDep, request: PostAccountRequest):
    """Testing: curl -H "Content-Type: application/json" -d "{\"name\":\"test\"}" http://localhost:8000/account"""
    with session.begin():
        new_account = Account(name=request.name)
        session.add(new_account)
        session.commit()

    return AccountData.model_validate(new_account, from_attributes=True)


@app.get("/accounts", response_model=List[AccountData])
async def get_accounts(session: SessionDep):
    """Testing: curl localhost:8000/accounts"""
    with session.begin():
        accounts: List[Account] = session.query(Account).all()
        convert_to_message = lambda account: AccountData.model_validate(
            account, from_attributes=True
        )
        return map(convert_to_message, accounts)


@app.post("/account/{account_id}/import")
async def import_csv(account_id: int, uploadFile: UploadFile, session: SessionDep):
    """Testing: curl -L -F "uploadFile=@test_data/sensitive/sample_transactions_checking.CSV" http://localhost:8000/account/1/import"""
    with uploadFile.file as binaryFile:

        # Persist file for reference.
        with session.begin():
            # TODO: Short-circuit if the file already exists (unique constraint maybe?)
            file = TransactionFile(
                filename=uploadFile.filename,
                data=binaryFile.read(),
            )
            session.add(file)
            session.commit()

        # Secondarily, parse file
        binaryFile.seek(0)
        with session.begin():
            transactions = parse_csv(binaryFile)
            for transaction in transactions:
                # TODO: Check to see if the transactions already exist!
                transaction.account_id = account_id
                session.add(transaction)
            session.commit()

        # TODO: Return a summary of the operations performed (# added, # skipped)
        return {"description": transactions[0].description, "total": len(transactions)}


@app.get("/account/{account_id}/transactions", response_model=GetTransactionsResponse)
async def get_transactions(
    session: SessionDep,
    account_id: int,
    page: int = 0,
    per_page: int = 20,
):

    # Persist file for reference.
    with session.begin():
        transactions = (
            session.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.post_date.desc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )

    transactionData = [
        TransactionData.model_validate(transaction, from_attributes=True)
        for transaction in transactions
    ]
    return GetTransactionsResponse(
        transactions=transactionData, page=page, per_page=per_page
    )


@app.put("/transactions", response_model=UpdateTransactionResponse)
async def update_transaction(session: SessionDep, request: UpdateTransactionRequest):
    # Persist file for reference.
    with session.begin():
        transaction = (
            session.query(Transaction)
            .filter(Transaction.id == request.transaction.id)
            .first()
        )
        if transaction is None:
            raise HTTPException(
                status_code=404, detail="Cannot find transaction to update"
            )

        if (
            transaction.account_id != request.transaction.account_id
            or transaction.amount != request.transaction.amount
            or transaction.description != request.transaction.description
            or transaction.post_date != request.transaction.post_date
            or transaction.init_date != request.transaction.init_date
        ):
            raise HTTPException(
                status_code=501,
                detail="Cannot change transaction fields outside of category",
            )

        if request.newCategoryName:
            if request.newSuperName:
                # Create new category AND new super
                new_super = Supercategory(name=request.newSuperName)
                category = Category(
                    name=request.newCategoryName, supercategory=new_super
                )
            elif request.superId:
                # Create new category with existing superId
                category = Category(
                    name=request.newCategoryName, supercategory_id=request.superId
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="must supply superId or newSuperName when providing newCategoryName",
                )
            transaction.category = category
        else:
            transaction.category_id = request.transaction.category_id
        session.flush()
        result = TransactionData.model_validate(transaction, from_attributes=True)

    return result


@app.get("/categories", response_model=GetCategoriesResponse)
async def getCategories(
    session: SessionDep,
):

    # Persist file for reference.
    with session.begin():
        categories = session.query(Category).order_by(Category.name.asc()).all()

        categoryData = [
            CategoryData.model_validate(category, from_attributes=True)
            for category in categories
        ]

        supercategories = (
            session.query(Supercategory).order_by(Supercategory.name.asc()).all()
        )

        superCategoryData = [
            SupercategoryData.model_validate(supercategory, from_attributes=True)
            for supercategory in supercategories
        ]

    return GetCategoriesResponse(
        categories=categoryData, superCategories=superCategoryData
    )


@app.post("/category", response_model=CategoryData)
async def post_category(session: SessionDep, request: PostCategoryRequest):

    new_category = Category(
        name=request.name, supercategory_id=request.supercategory_id
    )

    with session.begin():
        if request.supercategory_name:
            # If they submit a new supercategory name, create that too
            new_supercategory = Supercategory(name=request.supercategory_name)
            new_category.supercategory = new_supercategory

        session.add(new_category)
        session.commit()

    return AccountData.model_validate(new_category, from_attributes=True)


@app.put("/category", response_model=CategoryData)
async def update_category(session: SessionDep, request: CategoryData):
    with session.begin():
        category = session.get_one(Category, request.id)
        category.name = request.name

        if category.supercategory_id != request.supercategory_id:
            category.supercategory_id = request.supercategory_id

        category.rules.clear()

        for rule in request.rules:
            category.rules.append(
                Rule(contains=rule.contains, case_sensitive=rule.case_sensitive)
            )

        session.flush()
        session.refresh(category)
        result = CategoryData.model_validate(category, from_attributes=True)
        session.commit()

    return result


def start():
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
