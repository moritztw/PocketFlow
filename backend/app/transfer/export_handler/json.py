from sqlalchemy.orm import Session
from app.transfer.base import BaseExporter
from app.models.user import User

class JsonExporter(BaseExporter):
    def export(self, db: Session, user: User) -> dict:
        # Alle Daten des Users aus der DB laden
        data_raw = self.fetch_user_data(db, user)

        # als JSON ausgeben
        return {
            "version": "1.0",
            "username": user.username,
            "accounts": [{"id": a.id, "name": a.name} for a in data_raw["accounts"]],
            "budgets": [{"id": b.id, "name": b.name, "budget_type": b.budget_type, "rollover_enabled": b.rollover_enabled} for b in data_raw["budgets"]],
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in data_raw["tags"]],
            "scheduled_transactions": [
                {
                    "id": st.id,
                    "name": st.name,
                    "amount": st.amount,
                    "start_date": st.start_date.isoformat() if st.start_date else None,
                    "end_date": st.end_date.isoformat() if st.end_date else None,
                    "frequency": st.frequency,
                    "budget_id": st.budget_id,
                    "account_id": st.account_id
                } for st in data_raw["scheduled_transactions"]
            ],
            "transactions": [
                {
                    "id": tx.id,
                    "booking_date": tx.booking_date.isoformat() if tx.date else None,
                    "value_date": tx.value_date.isoformat() if tx.date else None,
                    "amount": tx.amount,
                    "purpose": tx.purpose,
                    "counterpart": tx.counterpart,
                    "iban": tx.iban,
                    "account_id": tx.account_id,
                    "budget_id": tx.budget_id
                } for tx in data_raw["transactions"]
            ]
        }
