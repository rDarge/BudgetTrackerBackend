from datetime import datetime
from typing import List

from pydantic import BaseModel


class ModelWithID(BaseModel):
    id: int

    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.id)


class AccountData(ModelWithID):
    name: str
    group: str


class TransactionData(ModelWithID):
    init_date: datetime | None = None
    post_date: datetime
    verified_at: datetime | None = None
    description: str
    amount: float
    account_id: int
    category_id: int | None = None


class PostAccountRequest(BaseModel):
    name: str
    group: str


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


class RuleData(BaseModel):
    contains: str
    case_sensitive: bool
    account_id: int


class CategoryData(ModelWithID):
    name: str
    supercategory_id: int
    rules: List[RuleData]


class SupercategoryData(ModelWithID):
    name: str


class GetCategoriesResponse(BaseModel):
    superCategories: List[SupercategoryData]
    categories: List[CategoryData]


class PostCategoryRequest(BaseModel):
    name: str
    supercategory_id: int | None
    supercategory_name: int | None


class UpdateCategoryRequest(BaseModel):
    id: int
    name: str
    supercategory_id: int
    rules: List[RuleData]


class ApplyRulesRequest(BaseModel):
    preview: bool


class TransactionUpdates(BaseModel):
    transaction: TransactionData
    old_category: str
    new_category: str


class ApplyRulesResponse(BaseModel):
    updated_transactions: List[TransactionUpdates]
