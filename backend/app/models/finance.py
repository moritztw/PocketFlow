from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.config_loader import load_config

# Config Datei Laden
config = load_config()
defaults = config.get("defaults", {})

# Verknpüfungstabelle für Tags (Many-to-Many)

budget_tags = Table(
    "budget_tags",
    Base.metadata,
    Column("budget_id", Integer, ForeignKey("budgets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

scheduled_transaction_tags = Table(
    "scheduled_transaction_tags",
    Base.metadata,
    Column("scheduled_transaction_id", Integer, ForeignKey("scheduled_transactions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column("transaction_id", Integer, ForeignKey("transactions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

# Hauptmodule für Finanzen:
# Account für die tatsächlichen physischen Konten
# Budget für die virtuellen Unterkonten
# ScheduledTransaction für geplante Transaktionen
# Transaction für die tatsächlichen Transaktionen

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    
    scheduled_transactions = relationship("ScheduledTransaction", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    budget_type = Column(String, nullable=False) # fix or flex
    rollover_enabled = Column(Boolean, default=defaults.get("rollover_enabled", True)) # Restgeld in den nächsten Monat mitnehmen. 
    # Default in Config setzen?

    scheduled_transactions = relationship("ScheduledTransaction", back_populates="budget")
    tags = relationship("Tag", secondary=budget_tags, backref="budgets")

    @property
    # Anfrage auch für frühere / zukünftige Monate möglich machen.
    def calculated_amount(self) -> float:
        return sum(st.amount for st in self.scheduled_transactions)

class ScheduledTransaction(Base):
    __tablename__ = "scheduled_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)

    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    frequency = Column(String, default=defaults.get("frequency", "monthly")) # daily, weekly, monthly, yearly

    account = relationship("Account", back_populates="scheduled_transactions")
    budget = relationship("Budget", back_populates="scheduled_transactions")
    tags = relationship("Tag", secondary=scheduled_transaction_tags, backref="scheduled_transactions")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)

    booking_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    purpose = Column(String, nullable=True)
    counterparty = Column(String, nullable=True)
    iban = Column(String, nullable=True)

    account = relationship("Account", back_populates="transactions")
    budget = relationship("Budget")
    tags = relationship("Tag", secondary=transaction_tags, backref="transactions")