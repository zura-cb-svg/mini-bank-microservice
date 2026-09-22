from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/accounts/", response_model=schemas.AccountResponse)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    new_account = models.Account(owner_name=account.owner_name, balance=account.balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@app.get("/accounts", response_model=list[schemas.AccountResponse])
def get_all_account(db: Session = Depends(get_db)):
    return db.query(models.Account).all()

@app.post("/transfer/")
def transfer_money(transfer: schemas.TransferCreate, db: Session = Depends(get_db)):
    sender = db.query(models.Account).filter(models.Account.id == transfer.from_account_id).first()
    receiver = db.query(models.Account).filter(models.Account.id == transfer.to_account_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Account not found")

    if sender.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Not enough money")

    if transfer.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    sender.balance -= transfer.amount
    receiver.balance += transfer.amount

    sender_tx = models.Transaction(
        amount=-transfer.amount,
        description=f"Transfer to Account {receiver.id}",
        account_id=sender.id
    )
    
    receiver_tx = models.Transaction(
        amount=transfer.amount,
        description=f"Received from Account {sender.id}",
        account_id=receiver.id
    )

    db.add(sender_tx)
    db.add(receiver_tx)
    db.commit()

    return {"message": "Transfer successful"}