from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag
from app.models.user import User
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
@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_account = Account(name=account_in.name, user_id=user.id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()

# Budgets
@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budgets(budget_in: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_budget = Budget(
        name=budget_in.name,
        budget_type=budget_in.budget_type,
        rollover_enabled=budget_in.rollover_enabled,
        user_id=user.id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/budgets", response_model=List[BudgetResponse])
def list_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Budget).filter(Budget.user_id == user.id).all()

# Sheduled Transaction
@router.post("/scheduled-transactions", response_model=ScheduledTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_transaction(st_in: ScheduledTransactionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Prüfen ob Budget und Account existieren und dem User gehören
    budget = db.query(Budget).filter(Budget.id == st_in.budget_id, Budget.user_id == user.id).first()
    account = db.query(Account).filter(Account.id == st_in.account_id, Account.user_id == user.id).first()
    
    if not budget or not account:
        raise HTTPException(status_code=400, detail="Invalid budget_id or account_id")

    db_st = ScheduledTransaction(
        name=st_in.name,
        amount=st_in.amount,
        start_date=st_in.start_date,
        end_date=st_in.end_date,
        frequency=st_in.frequency,
        budget_id=st_in.budget_id,
        account_id=st_in.account_id,
        user_id=user.id
    )
    db.add(db_st)
    db.commit()
    db.refresh(db_st)
    return db_st

@router.get("/scheduled-transactions", response_model=List[ScheduledTransactionResponse])
def list_scheduled_transactions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ScheduledTransaction).filter(ScheduledTransaction.user_id == user.id).all()
