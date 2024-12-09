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
post_collection = db['postDatabase']

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
    user = user_collection.find_one({"userEmail": email, "userPassword": password})
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
        "userName": user["userName"],
        "userEmail": user["userEmail"]
    }


@app.post("/createPost")
async def create_post(postTitle: str, postAuthor: str, postLLM: str, postNotes: str, postRating: str):
    post_data = {
        "postTitle": postTitle,
        "postAuthor": postAuthor,
        "postLLM": postLLM,
        "postNotes": postNotes,
        "postRating": postRating,
        "comments": []  
    }
    post_id = post_collection.insert_one(post_data).inserted_id
    return {"status": "Post created", "postId": str(post_id)}

@app.post("/updatePost")
async def update_post(postId: str, postTitle: str, postAuthor: str, postLLM: str, postNotes: str, postRating: str):
    update_data = {
        "postTitle": postTitle,
        "postAuthor": postAuthor,
        "postLLM": postLLM,
        "postNotes": postNotes,
        "postRating": postRating
    }

    result = post_collection.update_one(
        {"_id": ObjectId(postId)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return {"status": "Post updated", "postId": postId}

@app.post("/createComment")
async def create_comment(postId: str, commentNotes: str, commentAuthor: str):
    comment_data = {
        "commentId": str(ObjectId()), 
        "commentNotes": commentNotes,
        "commentAuthor": commentAuthor
    }
    result = post_collection.update_one(
        {"_id": ObjectId(postId)},
        {"$push": {"comments": comment_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    return {"status": "Comment added", "postId": postId}

@app.get("/getAllPosts")
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
    
    posts = list(post_collection.find(query))
    for post in posts:
        post["_id"] = str(post["_id"]) 
        for comment in post.get("comments", []):
            comment["commentId"] = str(comment["commentId"])
    
    return {"posts": posts}

@app.get("/getPost")
async def get_post(postId: str):
    post = post_collection.find_one({"_id": ObjectId(postId)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    post["_id"] = str(post["_id"])  
    for comment in post.get("comments", []):
        comment["commentId"] = str(comment["commentId"])
    
    return {"post": post}

@app.delete("/deletePost")
async def delete_post(postId: str):
    result = post_collection.delete_one({"_id": ObjectId(postId)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found.")

    return {"status": "Post deleted", "postId": postId}

@app.delete("/deleteComment")
async def delete_comment(postId: str, commentId: str):
    result = post_collection.update_one(
        {"_id": ObjectId(postId)},
        {"$pull": {"comments": {"commentId": commentId}}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found.")

    return {"status": "Comment deleted", "postId": postId, "commentId": commentId}