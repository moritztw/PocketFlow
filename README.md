# PocketFlow
Eine self-hosted, open source Webanwendung um Budgets, regelmäßige Ausgaben, Rücklagen und verfügbares Geld zu tracken.

## Features
- [ ] CSV Import von Bankdaten als Transactions
- [ ] Multi User pro Verwaltung (nicht länger 1 User = 1 Datensatz)
- [ ] Option einzelnen Scheduled_Transactions verschiedene Personen zuzuordnen, die es zahlen müssen 

## Backup / Import / Export
Alle Daten können als JSON Exportiert werden und ebenso importiert werden. Das Schema ist folgendes:

```
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PocketFlowBackup",
  "type": "object",
  "properties": {
    "version": { "type": "string" },
    "username": { "type": "string" },
    "accounts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" }
        },
        "required": ["id", "name"]
      }
    },
    "budgets": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "budget_type": { "type": "string" },
          "rollover_enabled": { "type": "boolean" }
        },
        "required": ["id", "name", "budget_type", "rollover_enabled"]
      }
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "color": { "type": ["string", "null"] }
        },
        "required": ["id", "name"]
      }
    },
    "scheduled_transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "amount": { "type": "number" },
          "start_date": { "type": ["string", "null"], "format": "date" },
          "end_date": { "type": ["string", "null"], "format": "date" },
          "frequency": { "type": "string" },
          "budget_id": { "type": "integer" },
          "account_id": { "type": "integer" }
        },
        "required": ["id", "name", "amount", "frequency", "budget_id", "account_id"]
      }
    },
    "transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "date": { "type": ["string", "null"], "format": "date" },
          "amount": { "type": "number" },
          "purpose": { "type": ["string", "null"] },
          "counterpart": { "type": ["string", "null"] },
          "account_id": { "type": "integer" },
          "budget_id": { "type": ["integer", "null"] }
        },
        "required": ["id", "amount", "account_id"]
      }
    }
  },
  "required": ["version", "username", "accounts", "budgets", "tags", "scheduled_transactions", "transactions"]
}
```