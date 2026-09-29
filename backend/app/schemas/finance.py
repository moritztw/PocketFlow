from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.config_loader import load_config

config = load_config()
defaults = config.get("defaults", {})

# Tag Schemas 
class TagBase(BaseModel):
    name: str
    color: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class TagResponse(TagBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Account Schema
class AccountBase(BaseModel):
    name: str

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None

class AccountResponse(AccountBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Budget Schema
class BudgetBase(BaseModel):
    name: str
    budget_type: str = Field(default=defaults.get("default_budget_type", "flex"))
    rollover_enabled: bool = Field(default=defaults.get("budget_rollover_enabled", True))

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    budget_type: Optional[str] = None
    rollover_enabled: Optional[bool] = None

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    calculated_amount: float
    class Config:
        from_attributes = True

# Scheduled Transaction Schema
class ScheduledTransactionBase(BaseModel):
    name: str
    amount: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: str = Field(default=defaults.get("schedules_transaction_frequency", "monthly"))
    budget_id: int
    account_id: int

class ScheduledTransactionCreate(ScheduledTransactionBase):
    pass

class ScheduledTransactionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: Optional[str] = None
    budget_id: Optional[int] = None
    account_id: Optional[int] = None

class ScheduledTransactionResponse(ScheduledTransactionBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# Transactions
class TransactionBase(BaseModel):
    date: Optional[date] = None
    amount: float
    purpose: Optional[str] = None
    counterpart: Optional[str] = None
    account_id: int
    budget_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    purpose: Optional[str] = None
    counterpart: Optional[str] = None
    account_id: Optional[int] = None
    budget_id: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  