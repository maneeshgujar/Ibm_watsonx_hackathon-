from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid

app = FastAPI(
    title="Customer Asset Allocation API",
    description="Simple API exposing customer profiles and their asset allocations (mutual funds, bonds, equity, crypto). Supports read, create and update operations.",
    version="1.0.0"
)


# ------------------------------------------------
# In-memory stores
# ------------------------------------------------

customers: Dict[str, dict] = {}
allocations: Dict[str, dict] = {}
goals: Dict[str, dict] = {}


# ------------------------------------------------
# Models
# ------------------------------------------------


class CustomerCreateRequest(BaseModel):
    name: str
    age: int
    email: str
    phone: Optional[str] = None


class Customer(BaseModel):
    customerId: str
    name: str
    age: int
    email: str
    phone: Optional[str] = None
    createdAt: str


class AssetItem(BaseModel):
    name: str
    quantity: float
    price: float


class AssetAllocation(BaseModel):
    customerId: str
    mutual_funds: List[AssetItem] = []
    bonds: List[AssetItem] = []
    equity: List[AssetItem] = []
    crypto: List[AssetItem] = []
    # percentages are derived fields but allow client to supply an optional breakdown
    allocation_percentages: Optional[Dict[str, float]] = None


class AllocationUpsertRequest(BaseModel):
    customerId: str
    mutual_funds: Optional[List[AssetItem]] = None
    bonds: Optional[List[AssetItem]] = None
    equity: Optional[List[AssetItem]] = None
    crypto: Optional[List[AssetItem]] = None
    allocation_percentages: Optional[Dict[str, float]] = None


class GoalRequest(BaseModel):
    customerId: str
    name: str
    goal_amount: float
    period_months: int


class GoalRecord(BaseModel):
    customerId: str
    name: str
    goal_amount: float
    period_months: int
    createdAt: str


# ------------------------------------------------
# Helper functions
# ------------------------------------------------


def ensure_customer_exists(cid: str):
    if cid not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")


# ------------------------------------------------
# Endpoints: customers and allocations
# ------------------------------------------------


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(req: CustomerCreateRequest):
    cid = "CUST" + uuid.uuid4().hex[:8].upper()
    c = Customer(
        customerId=cid,
        name=req.name,
        age=req.age,
        email=req.email,
        phone=req.phone,
        createdAt=datetime.utcnow().isoformat()
    )
    customers[cid] = c.dict()
    return c


@app.get("/customers/{customerId}", response_model=Customer)
def get_customer(customerId: str):
    ensure_customer_exists(customerId)
    return customers[customerId]


@app.put("/customers/{customerId}", response_model=Customer)
def update_customer(customerId: str, req: CustomerCreateRequest):
    ensure_customer_exists(customerId)
    # update fields
    cust = customers[customerId]
    cust["name"] = req.name
    cust["age"] = req.age
    cust["email"] = req.email
    cust["phone"] = req.phone
    customers[customerId] = cust
    return cust


@app.get("/customers/{customerId}/allocation", response_model=AssetAllocation)
def get_allocation(customerId: str):
    ensure_customer_exists(customerId)
    if customerId not in allocations:
        raise HTTPException(status_code=404, detail="Allocation not found for customer")
    return allocations[customerId]


@app.post("/customers/{customerId}/allocation", response_model=AssetAllocation, status_code=201)
def create_allocation(customerId: str, req: AllocationUpsertRequest):
    ensure_customer_exists(customerId)
    if req.customerId != customerId:
        raise HTTPException(status_code=400, detail="Customer ID mismatch between path and body")
    alloc = AssetAllocation(
        customerId=customerId,
        mutual_funds=req.mutual_funds or [],
        bonds=req.bonds or [],
        equity=req.equity or [],
        crypto=req.crypto or [],
        allocation_percentages=req.allocation_percentages
    )
    allocations[customerId] = alloc.dict()
    return alloc


@app.put("/customers/{customerId}/allocation", response_model=AssetAllocation)
def update_allocation(customerId: str, req: AllocationUpsertRequest):
    ensure_customer_exists(customerId)
    if req.customerId != customerId:
        raise HTTPException(status_code=400, detail="Customer ID mismatch between path and body")
    if customerId not in allocations:
        raise HTTPException(status_code=404, detail="Allocation not found for customer")
    # merge/update provided fields
    existing = allocations[customerId]
    if req.mutual_funds is not None:
        existing["mutual_funds"] = [a.dict() for a in req.mutual_funds]
    if req.bonds is not None:
        existing["bonds"] = [a.dict() for a in req.bonds]
    if req.equity is not None:
        existing["equity"] = [a.dict() for a in req.equity]
    if req.crypto is not None:
        existing["crypto"] = [a.dict() for a in req.crypto]
    if req.allocation_percentages is not None:
        existing["allocation_percentages"] = req.allocation_percentages
    allocations[customerId] = existing
    return existing


@app.post("/customers/{customerId}/goals", response_model=GoalRecord, status_code=201)
def add_goal(customerId: str, req: GoalRequest):
    ensure_customer_exists(customerId)
    if req.customerId != customerId:
        raise HTTPException(status_code=400, detail="Customer ID mismatch between path and body")
    gid = "GOAL" + uuid.uuid4().hex[:8].upper()
    g = GoalRecord(
        customerId=customerId,
        name=req.name,
        goal_amount=req.goal_amount,
        period_months=req.period_months,
        createdAt=datetime.utcnow().isoformat()
    )
    # allow multiple goals per customer; store as dict of lists
    if customerId not in goals:
        goals[customerId] = []
    goals[customerId].append(g.dict())
    return g


@app.get("/customers/{customerId}/goals", response_model=List[GoalRecord])
def get_goals(customerId: str):
    ensure_customer_exists(customerId)
    return goals.get(customerId, [])


