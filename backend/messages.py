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


class UpdateTransactionRequest(BaseModel):
    transaction: TransactionData
    newCategoryName: str | None = None
    superId: int | None = None
    newSuperName: str | None = None


class UpdateTransactionResponse(TransactionData):
    pass


class GetTransactionsResponse(BaseModel):
    transactions: List[TransactionData]
    page: int
    per_page: int


class CategoryData(ModelWithID):
    name: str
    supercategory_id: int


class SupercategoryData(ModelWithID):
    name: str


class GetCategoriesResponse(BaseModel):
    superCategories: List[SupercategoryData]
    categories: List[CategoryData]


class PostCategoryRequest(BaseModel):
    name: str
    supercategory_id: int | None
    supercategory_name: int | None
