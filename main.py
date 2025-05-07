from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
import json

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["car_database"]
collection = db["cars"]

@app.get("/cars/{car_id}")
def get_car(car_id: str):
    try:
        car = collection.find_one({"_id": ObjectId(car_id)})
        if car:
            return json.loads(dumps(car))
        else:
            raise HTTPException(status_code=404, detail="Car not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or DB error: {e}")
