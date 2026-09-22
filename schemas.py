from pydantic import BaseModel

class AccountCreate(BaseModel):
    owner_name: str
    balance: int


class TransactionResponse(BaseModel):
    id: int
    amount: int
    description: str

    model_config = {"from_attributes": True}


class AccountResponse(BaseModel):
    id: int
    owner_name: str
    balance: int
    transactions: list[TransactionResponse] = []
    
    model_config = {"from_attributes": True}


class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: int