# Customer Asset Allocation API

Lightweight FastAPI mock of customer profiles, asset allocations (mutual funds, bonds, equity, crypto) and customer goals. Designed for local development, demos and integration with automation/orchestrator agents (no authentication).

## Requirements
- Python 3.8+
- Install deps:
```bash
pip install fastapi uvicorn pydantic
```

## Run locally
From the project folder:
```powershell
# start server
uvicorn simple_bank_api:app --reload --host 0.0.0.0 --port 8000
```
Base URL: `http://localhost:8000`

Expose publicly (optional): use ngrok or Replit. Example ngrok:
```powershell
# after ngrok authtoken setup
ngrok http 8000
```

## Endpoints

1. Create customer
- POST /customers
- Body (JSON):
```json
{
  "name": "Alice Patel",
  "age": 34,
  "email": "alice.patel@example.com",
  "phone": "555-0101"
}
```
- Returns created customer with `customerId` and `createdAt`.

2. Get customer
- GET /customers/{customerId}

3. Update customer
- PUT /customers/{customerId}
- Body same as create

4. Create / Replace allocation
- POST /customers/{customerId}/allocation
- Body (JSON):
```json
{
  "customerId": "CUSTXXXXXXXX",
  "mutual_funds": [ { "name": "Global Equity Fund", "quantity": 120.5, "price": 25.3 } ],
  "bonds": [ { "name": "US Treasury 5Y", "quantity": 10, "price": 1020.0 } ],
  "equity": [ { "name": "AAPL", "quantity": 15, "price": 185.5 } ],
  "crypto": [ { "name": "BTC", "quantity": 0.02, "price": 62000.0 } ],
  "allocation_percentages": { "mutual_funds": 40, "bonds": 20, "equity": 35, "crypto": 5 }
}
```

5. Get allocation
- GET /customers/{customerId}/allocation

6. Update allocation (partial)
- PUT /customers/{customerId}/allocation
- Body fields optional; only provided fields are merged/updated.
```json
{
  "customerId": "CUSTXXXXXXXX",
  "crypto": [ { "name": "ETH", "quantity": 0.5, "price": 1800.0 } ],
  "allocation_percentages": { "mutual_funds": 38, "bonds": 20, "equity": 37, "crypto": 5 }
}
```

7. Add goal
- POST /customers/{customerId}/goals
- Body:
```json
{
  "customerId": "CUSTXXXXXXXX",
  "name": "Down payment for house",
  "goal_amount": 50000.0,
  "period_months": 48
}
```

8. Get goals
- GET /customers/{customerId}/goals

## Examples (curl)
Create customer:
```bash
curl -X POST http://localhost:8000/customers -H "Content-Type: application/json" -d '{"name":"Rahul","age":45,"email":"rahul@example.com","phone":"56784334"}'
```

Add allocation:
```bash
curl -X POST http://localhost:8000/customers/CUSTABC123/allocation -H "Content-Type: application/json" -d @allocation.json
```

Add goal:
```bash
curl -X POST http://localhost:8000/customers/CUSTABC123/goals -H "Content-Type: application/json" -d '{"customerId":"CUSTABC123","name":"Retirement","goal_amount":200000,"period_months":240}'
```

## Integration notes for orchestrator/agent
- Use POST /customers to create and capture `customerId`.
- For automation, use GET /customers/{customerId}/allocation and GET /customers/{customerId}/goals to fetch current state.
- The update endpoints accept partial updates (PUT /allocation merges provided fields).
- No authentication — be cautious when exposing publicly.

## Data persistence
- In-memory only. Data resets on process restart. For persistence, replace in-memory stores with a DB layer.

## Contacts / Next steps
- Add validation rules for allocation_percentages (sum to ~100).
- Add basic simulation code to estimate goal achievement (can be integrated with `rebalancing_rules.txt
