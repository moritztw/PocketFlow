from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag
from models.user import User
from app.schemas.finance import (
    AccountCreate,
    AccountResponse,
    BudgetCreate,
    BudgetResponse,
    ScheduledTransactionCreate,
    ScheduledTransactionResponse,
    TagCreate,
    TagResponse
)

router = APIRouter(prefix="/api/v1", tags=["PocketFlow Finance API"])

# Hilfsfunktion um aktuell immer den Admin als Login zu nutzen, da es noch keine Authentifizierung gibt
def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return user

# Accounts
@post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db), User = Depends(get_current_user)):
    db_account = Account(name=account_in.name, user_id=user.id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depens(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()

# Budgets