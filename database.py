from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

def get_mongo_client():
    return MongoClient(os.getenv("MONGO_URI"))

def get_user_by_id(user_id):
    with get_mongo_client() as client:
        db = client.apartments
        users_collection = db.users
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    return user_data
