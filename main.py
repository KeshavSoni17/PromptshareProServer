from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional

# MongoDB connection
client = MongoClient("mongodb://mongo:wPtlHWqUmHUpGKInIannYebRZJzsejaL@junction.proxy.rlwy.net:21099")
db = client["PromptsharePro"]  # Replace with your database name
users_collection = db["userDatabase"]  # Collection for users
posts_collection = db["postDatabase"]  # Collection for posts

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

def post_to_dict(post):
    post["_id"] = str(post["_id"])
    return post

@app.post("/posts/")
async def create_post(title: str, author: str, llm: str, notes: str, rating: int):
    post_data = {
        "postTitle": title,
        "postAuthor": author,
        "postLLM": llm,
        "postNotes": notes,
        "postRating": rating,
        "comments": []
    }
    result = posts_collection.insert_one(post_data)
    return {"message": "Post created successfully", "post_id": str(result.inserted_id)}

@app.get("/posts/", response_model=List[dict])
async def get_all_posts(filter: Optional[str] = ""):
    query = {}
    if filter:
        query = {
            "$or": [
                {"postTitle": {"$regex": filter, "$options": "i"}},
                {"postAuthor": {"$regex": filter, "$options": "i"}},
                {"postLLM": {"$regex": filter, "$options": "i"}},
                {"postNotes": {"$regex": filter, "$options": "i"}}
            ]
        }
    posts = posts_collection.find(query)
    return [post_to_dict(post) for post in posts]

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        return post_to_dict(post)
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = posts_collection.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count:
        return {"message": "Post deleted successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/comments/")
async def create_comment(post_id: str, comment_id: str, comment_notes: str, comment_author: str):
    comment_data = {
        "commentId": comment_id,
        "commentNotes": comment_notes,
        "commentAuthor": comment_author
    }
    result = posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment_data}}
    )
    if result.matched_count:
        return {"message": "Comment added successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str):
    result = posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"commentId": comment_id}}}
    )
    if result.matched_count:
        return {"message": "Comment deleted successfully"}
    raise HTTPException(status_code=404, detail="Post or comment not found")
