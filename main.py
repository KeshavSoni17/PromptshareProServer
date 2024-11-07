from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb://mongo:wPtlHWqUmHUpGKInIannYebRZJzsejaL@junction.proxy.rlwy.net:21099")
db = client["PromptsharePro"]  # Replace with your database name
users_collection = db["userDatabase"]  # Collection for users

app = FastAPI()

# Pydantic model for User
class User(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    user_password: str

@app.post("/register")
async def register_user(user: User):
    if users_collection.find_one({"user_id": user.user_id}):
        raise HTTPException(status_code=400, detail="User with this ID already exists")
    
    users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(email: str, password: str):
    user = users_collection.find_one({"user_email": email, "user_password": password})
    if user:
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return {"user": user}
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
