from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient
from bson import ObjectId
import certifi
from typing import List
from pydantic import BaseModel
from Schema.user import User
from db.config import MONGO_URI
custom_title = "TT DevOps Hari - PYTHON MICROSERVICES - CRUD"
app = FastAPI(title=custom_title,openapi_url="/hari.json"  )

client = MongoClient(MONGO_URI,tlsCAFile=certifi.where())
db = client["cmd"]
users_collection = db["todo"]

@app.get("/api/v1/users", response_model=List[User],tags=["User-Microservices"])
async def get_users():
    users = list(users_collection.find())
    user_objects = []
    for user in users:
        if 'name' in user and 'email' in user:
            user_objects.append(User(**user))
    
    return user_objects

@app.post("/api/v1/user", response_model=User,tags=["User-Microservices"])
async def add_user(user: User):
    user_dict = user.dict()
    user_id = users_collection.insert_one(user_dict).inserted_id
    return {**user_dict, "id": str(user_id)}

@app.get("/api/v1/user/{id}", response_model=User,tags=["User-Microservices"])
async def get_user(id: str):
    user = users_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/api/v1/user/{id}", response_model=User,tags=["User-Microservices"])
async def update_user(id: str, user: User):
    user_dict = user.dict()
    result = users_collection.update_one({"_id": ObjectId(id)}, {"$set": user_dict})
    if result.modified_count == 1:
        return {**user_dict, "id": id}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.delete("/api/v1/user/{id}",tags=["User-Microservices"])
async def delete_user(id: str):
    result = users_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
