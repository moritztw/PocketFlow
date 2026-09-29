from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag
from app.models.user import User
from app.schemas.finance import (
    AccountCreate, AccountUpdate, AccountResponse,
    BudgetCreate, BudgetUpdate, BudgetResponse,
    ScheduledTransactionCreate, ScheduledTransactionUpdate, ScheduledTransactionResponse,
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TagCreate, TagUpdate, TagResponse
)

router = APIRouter(prefix="/api/v1", tags=["PocketFlow Finance API"])

# Hilfsfunktion um aktuell immer den Admin als Login zu nutzen, da es noch keine Authentifizierung gibt
def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    return user

# Tags
@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    # Optional: Prüfen, ob ein Tag mit dem Namen für diesen User schon existiert
    existing = db.query(Tag).filter(Tag.user_id == user.id, Tag.name == tag_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")

    db_tag = Tag(
        name=tag_in.name,
        color=tag_in.color,
        user_id=user.id
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.patch("/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_in: TagUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    for key, value in tag_in.dict(exclude_unset=True).items():
        setattr(db_tag, key, value)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags", response_model=List[TagResponse])
def list_tags(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    return db.query(Tag).filter(Tag.user_id == user.id).all()

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user.id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(db_tag)
    db.commit()
    return None

# Accounts
@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_account = Account(name=account_in.name, user_id=user.id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.patch("/accounts/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_in: AccountUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for key, value in account_in.dict(exclude_unset=True).items():
        setattr(db_account, key, value)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()

@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(db_account)
    db.commit()
    return None

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

@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget_in: BudgetUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    for key, value in budget_in.dict(exclude_unset=True).items():
        setattr(db_budget, key, value)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/budgets", response_model=List[BudgetResponse])
def list_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Budget).filter(Budget.user_id == user.id).all()

@router.delete("/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(db_budget)
    db.commit()
    return None

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

@router.patch("/scheduled-transactions/{st_id}", response_model=ScheduledTransactionResponse)
def update_scheduled_transaction(st_id: int, st_in: ScheduledTransactionUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_st = db.query(ScheduledTransaction).filter(ScheduledTransaction.id == st_id, ScheduledTransaction.user_id == user.id).first()
    if not db_st:
        raise HTTPException(status_code=404, detail="Scheduled Transaction not found")
    
    for key, value in st_in.dict(exclude_unset=True).items():
        setattr(db_st, key, value)
    db.commit()
    db.refresh(db_st)
    return db_st

@router.get("/scheduled-transactions", response_model=List[ScheduledTransactionResponse])
def list_scheduled_transactions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ScheduledTransaction).filter(ScheduledTransaction.user_id == user.id).all()

@router.delete("/scheduled-transactions/{st_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_transaction(
    st_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_st = db.query(ScheduledTransaction).filter(ScheduledTransaction.id == st_id, ScheduledTransaction.user_id == user.id).first()
    if not db_st:
        raise HTTPException(status_code=404, detail="Scheduled Transaction not found")
    
    db.delete(db_st)
    db.commit()
    return None

# Transactions
@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_transaction = Transaction(
        date=transaction_in.date,
        amount=transaction_in.amount,
        purpose=transaction_in.purpose,
        counterpart=transaction_in.counterpart,
        account_id=transaction_in.account_id,
        budget_id=transaction_in.budget_id,
        user_id=user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, transaction_in: TransactionUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    for key, value in transaction_in.dict(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    return db.query(Transaction).filter(Transaction.user_id == user.id).all()

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user.id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return None