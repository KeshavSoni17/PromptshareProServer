from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId

app = FastAPI()

client = MongoClient("mongodb://mongo:wPtlHWqUmHUpGKInIannYebRZJzsejaL@junction.proxy.rlwy.net:21099")
db = client['main']
user_collection = db['userDatabase']

@app.post("/registerUser")
async def register_user(username: str, email: str, password: str):
    if user_collection.find_one({"userEmail": email}):
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    user_id = user_collection.insert_one({
        "userName": username,
        "userEmail": email,
        "userPassword": password
    }).inserted_id
    
    return {"status": "User registered", "userId": str(user_id)}

@app.post("/loginUser")
async def login_user(email: str, password: str):
    user = user_collection.find_one({"email": email, "password": password})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {"status": "Login successful", "userId": str(user["_id"])}

@app.get("/getUserByEmail")
async def get_user_by_email(email: str):
    user = user_collection.find_one({"userEmail": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return {
        "userId": str(user["_id"]),
        "userName": user["username"],
        "userEmail": user["email"]
    }
