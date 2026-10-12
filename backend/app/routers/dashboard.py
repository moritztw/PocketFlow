from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.routers.finance import get_current_user
from app.models.finance import Account, Budget, Transaction

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Summary"])

@router.get("/accounts-summary")
def get_accounts_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Liefert alle Konten des Users inklusive des aktuellen Kontostands (Summe aller Transaktionen)."""
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    
    result = []
    for acc in accounts:
        # Summe aller Transaktionen für dieses Konto berechnen
        balance_sum = db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == acc.id,
            Transaction.user_id == user.id
        ).scalar() or 0.0

        result.append({
            "id": acc.id,
            "name": acc.name,
            "balance": round(balance_sum, 2)
        })
        
    return result


@router.get("/budgets-summary")
def get_budgets_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Liefert eine Übersicht aller Budgets und zeigt, wie viel Geld bereits ausgegeben wurde."""
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    
    result = []
    for b in budgets:
        # Summe der Ausgaben (negative Beträge oder alle Transaktionen in diesem Budget)
        spent_sum = db.query(func.sum(Transaction.amount)).filter(
            Transaction.budget_id == b.id,
            Transaction.user_id == user.id
        ).scalar() or 0.0

        result.append({
            "id": b.id,
            "name": b.name,
            "budget_type": b.budget_type,
            "rollover_enabled": b.rollover_enabled,
            "total_spent": round(spent_sum, 2)
        })
        
    return result


@router.get("/monthly-overview")
def get_monthly_overview(
    year: int = Query(..., description="Jahr, z.B. 2026"),
    month: int = Query(..., description="Monat (1-12)"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Gibt Einnahmen, Ausgaben und die Bilanz für einen spezifischen Monat aus."""
    # Start- und Enddatum für den Monat generieren
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day}"

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.booking_date >= start_date,
        Transaction.booking_date <= end_date
    ).all()

    income = sum(tx.amount for tx in transactions if tx.amount > 0)
    expenses = sum(tx.amount for tx in transactions if tx.amount < 0)
    net = income + expenses  # da expenses negativ sind

    return {
        "year": year,
        "month": month,
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "net_balance": round(net, 2),
        "transaction_count": len(transactions)
    }