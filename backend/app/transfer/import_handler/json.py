import json
from datetime import date
from sqlalchemy.orm import Session
from app.transfer.base import BaseImporter
from app.models.finance import Account, Budget, ScheduledTransaction, Transaction, Tag
from app.models.user import User

class JsonImporter(BaseImporter):
    def parse(self, file_content: bytes) -> dict:
        return json.loads(file_content.decode("utf-8"))

    def save_to_db(self, db: Session, user: User, data: dict) -> None:
        account_map = {}
        budget_map = {}

        # Hilfsfunktion, um Accounts aufzulösen
        def resolve_account_id(acc_id_from_json):
            if not acc_id_from_json:
                return None
            if acc_id_from_json in account_map:
                return account_map[acc_id_from_json]
            
            existing_acc = db.query(Account).filter(Account.id == acc_id_from_json, Account.user_id == user.id).first()
            if existing_acc:
                return existing_acc.id
            
            first_acc = db.query(Account).filter(Account.user_id == user.id).first()
            return first_acc.id if first_acc else None

        # Hilfsfunktion, um Budgets aufzulösen oder automatisch anzulegen
        def resolve_or_create_budget(budget_id_from_json, fallback_name="Sonstiges"):
            # 1. Versuche über ID-Mapping
            if budget_id_from_json and budget_id_from_json in budget_map:
                return budget_map[budget_id_from_json]
            
            # 2. Versuche über direkte ID in DB
            if budget_id_from_json:
                existing_budget = db.query(Budget).filter(Budget.id == budget_id_from_json, Budget.user_id == user.id).first()
                if existing_budget:
                    return existing_budget.id

            # 3. Fallback: Suche nach einem Budget mit dem Namen der wiederkehrenden Ausgabe
            if fallback_name:
                existing_by_name = db.query(Budget).filter(Budget.name == fallback_name, Budget.user_id == user.id).first()
                if existing_by_name:
                    return existing_by_name.id
                
                # Wenn auch das nicht existiert: Automatisch als Budget anlegen!
                new_budget = Budget(
                    name=fallback_name,
                    budget_type="fix",  # Wiederkehrende Ausgaben sind meist Fixkosten
                    rollover_enabled=False,
                    user_id=user.id
                )
                db.add(new_budget)
                db.commit()
                db.refresh(new_budget)
                return new_budget.id

            return None

        # 1. Accounts importieren (falls im JSON enthalten)
        if "accounts" in data:
            for acc_data in data["accounts"]:
                existing = db.query(Account).filter(Account.user_id == user.id, Account.name == acc_data["name"]).first()
                if not existing:
                    new_acc = Account(name=acc_data["name"], user_id=user.id)
                    db.add(new_acc)
                    db.commit()
                    db.refresh(new_acc)
                    account_map[acc_data["id"]] = new_acc.id
                else:
                    account_map[acc_data["id"]] = existing.id

        # 2. Budgets importieren (falls im JSON enthalten)
        if "budgets" in data:
            for b_data in data["budgets"]:
                existing = db.query(Budget).filter(Budget.user_id == user.id, Budget.name == b_data["name"]).first()
                if not existing:
                    new_b = Budget(
                        name=b_data["name"],
                        budget_type=b_data.get("budget_type", "flex"),
                        rollover_enabled=b_data.get("rollover_enabled", False),
                        user_id=user.id
                    )
                    db.add(new_b)
                    db.commit()
                    db.refresh(new_b)
                    budget_map[b_data["id"]] = new_b.id
                else:
                    budget_map[b_data["id"]] = existing.id

        # 3. Tags importieren (falls im JSON enthalten)
        if "tags" in data:
            for t_data in data["tags"]:
                existing = db.query(Tag).filter(Tag.user_id == user.id, Tag.name == t_data["name"]).first()
                if not existing:
                    new_t = Tag(
                        name=t_data["name"],
                        color=t_data.get("color"),
                        user_id=user.id
                    )
                    db.add(new_t)
                    db.commit()

        # 4. Scheduled Transactions importieren (mit automatischem Budget-Fallback)
        if "scheduled_transactions" in data:
            for st_data in data["scheduled_transactions"]:
                mapped_account_id = resolve_account_id(st_data.get("account_id"))
                
                # Hier greift die neue Logik: Wenn kein Budget gefunden wird, 
                # wird ein Budget mit dem Namen der Scheduled Transaction angelegt.
                st_name = st_data.get("name", "Unbekannt")
                mapped_budget_id = resolve_or_create_budget(st_data.get("budget_id"), fallback_name=st_name)
                
                if mapped_account_id and mapped_budget_id:
                    new_st = ScheduledTransaction(
                        name=st_name,
                        amount=st_data["amount"],
                        start_date=date.fromisoformat(st_data["start_date"]) if st_data.get("start_date") else None,
                        end_date=date.fromisoformat(st_data["end_date"]) if st_data.get("end_date") else None,
                        frequency=st_data.get("frequency", "monthly"),
                        budget_id=mapped_budget_id,
                        account_id=mapped_account_id,
                        user_id=user.id
                    )
                    db.add(new_st)

        # 5. Reguläre Transaktionen importieren (falls im JSON enthalten)
        if "transactions" in data:
            for tx_data in data["transactions"]:
                mapped_account_id = resolve_account_id(tx_data.get("account_id"))
                mapped_budget_id = resolve_or_create_budget(tx_data.get("budget_id"), fallback_name=None)

                if mapped_account_id:
                    new_tx = Transaction(
                        date=date.fromisoformat(tx_data["date"]) if tx_data.get("date") else None,
                        amount=tx_data["amount"],
                        purpose=tx_data.get("purpose"),
                        counterpart=tx_data.get("counterpart"),
                        account_id=mapped_account_id,
                        budget_id=mapped_budget_id,
                        user_id=user.id
                    )
                    db.add(new_tx)
        
        db.commit()