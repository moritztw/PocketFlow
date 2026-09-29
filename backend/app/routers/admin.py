from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.finance import get_current_user
from app.models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Management"])

@router.delete("/reset-data", status_code=status.HTTP_204_NO_CONTENT)
def reset_user_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Löscht alle Finanzdaten des aktuellen Users (Transaktionen, Budgets, Konten etc.)."""
    
    # In korrekter Reihenfolge löschen (wegen Foreign Keys)
    db.query(Transaction).filter(Transaction.user_id == user.id).delete()
    db.query(ScheduledTransaction).filter(ScheduledTransaction.user_id == user.id).delete()
    db.query(Budget).filter(Budget.user_id == user.id).delete()
    db.query(Tag).filter(Tag.user_id == user.id).delete()
    db.query(Account).filter(Account.user_id == user.id).delete()
    
    db.commit()
    return None