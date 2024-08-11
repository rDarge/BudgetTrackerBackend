from datetime import datetime
from typing import List
from pydantic import BaseModel


class ModelWithID(BaseModel):
    id: int

    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.id)


class AccountData(ModelWithID):
    name: str


class TransactionData(ModelWithID):
    init_date: datetime | None = None
    post_date: datetime
    description: str
    amount: float
    account_id: int
    category_id: int | None = None


class PostAccountRequest(BaseModel):
    name: str


class GetAccountsResponse(BaseModel):
    accounts: List[AccountData]


class GetTransactionsResponse(BaseModel):
    transactions: List[TransactionData]
    page: int
    per_page: int
