from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag

class BaseImporter(ABC):
    @abstractmethod
    def parse(self, file_content: bytes) -> Dict[str, any]:
        # Liest Rohdaten (Bytes) ein und gibt ein Dict zurück
        pass

    @abstractmethod
    def save_to_db(self, db: Session, user: User, data: Dict[str, any]) -> None:
        # Speichert die strukturierten Dict Daten in der DB
        pass

class BaseExporter(ABC):
    def fetch_user_data(self, db: Session, user: User) -> Dict[str, list]:
        #Daten für alle Exporte zusammenstellen
        return{
            "accounts": db.query(Account).filter(Account.user_id == user.id).all(),
            "budgets": db.query(Budget).filter(Budget.user_id == user.id).all(),
            "tags": db.query(Tag).filter(Tag.user_id == user.id).all(),
            "scheduled_transactions": db.query(ScheduledTransaction).filter(ScheduledTransaction.user_id == user.id).all(),
            "transactions": db.query(Transaction).filter(Transaction.user_id == user.id).all()        }

    @abstractmethod
    def export(self, db: Session, user: User) -> Any:
        # Holt die Daten des Users aus der DB und bereitet sie für den Export auf
        pass