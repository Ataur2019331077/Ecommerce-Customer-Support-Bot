from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Dict, Any
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()
import os
import random
from typing import Optional



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["open-ecommerce"]
order_db = db["orders"]
complaint_db = db["complaints"]
shipping_db = db["shipping"]





@app.get("/order/{orderId}", response_model=List[Dict[str, Any]])
def get_order(orderId: str):
    """Fetch order details by orderId."""
    order = order_db.find_one({"orderId": orderId})
    if not order:
        return []
    order["_id"] = str(order["_id"])
    return [order]

class Complaint(BaseModel):
    orderId: str
    complaint: str
@app.post("/complaint", response_model=Dict[str, Any])
def create_complaint(complaint: Complaint):
    """Create a new complaint."""
    issue_token = str(random.randint(100000, 999999))
    complaint_data = {
        "orderId": complaint.orderId,
        "complaint": complaint.complaint,
        "issue_token": issue_token,
        "status": "pending"
    }
    result = complaint_db.insert_one(complaint_data)
    return {"id": str(result.inserted_id), "message": "Complaint created successfully."}



class Shipping(BaseModel):
    orderId: str
    delivery_date: Optional[str] = None 
    delivery_address: str
@app.put("/shipping/{orderId}", response_model=Dict[str, Any])
def update_shipping(orderId: str, shipping: Shipping):
    """Update shipping details for an order."""
    shipping_data = {
        "orderId": shipping.orderId,
        "delivery_date": shipping.delivery_date,
        "delivery_address": shipping.delivery_address
    }
    result = shipping_db.update_one({"orderId": orderId}, {"$set": shipping_data}, upsert=True)
    if result.modified_count > 0 or result.upserted_id:
        return {"message": "Shipping details updated successfully."}
    else:
        return {"message": "No changes made to the shipping details."}