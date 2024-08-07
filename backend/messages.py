from typing import List
from pydantic import BaseModel


class AccountData(BaseModel):
    id: int
    name: str

    def __hash__(self):  # make hashable BaseModel subclass
        return hash(self.id)


class PostAccountRequest(BaseModel):
    name: str


class GetAccountsResponse(BaseModel):
    accounts: List[AccountData]
