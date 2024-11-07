from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb://mongo:wPtlHWqUmHUpGKInIannYebRZJzsejaL@junction.proxy.rlwy.net:21099")
db = client["PromptsharePro"]  # Replace with your database name
users_collection = db["userDatabase"]  # Collection for users

app = FastAPI()

@app.post("/register")
async def register_user(user_id: str, user_name: str, user_email: str, user_password: str):
    if users_collection.find_one({"user_id": user_id}):
        raise HTTPException(status_code=400, detail="User with this ID already exists")
    
    user_data = {
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user_email,
        "user_password": user_password
    }
    
    users_collection.insert_one(user_data)
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
        # Convert the MongoDB document to a dictionary and remove ObjectId
        user["_id"] = str(user["_id"])  # Convert ObjectId to string if needed
        return {"user": user}
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    result = users_collection.delete_one({"user_id": user_id})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
