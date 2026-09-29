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

class ScheduledTransactionResponse(ScheduledTransactionBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True