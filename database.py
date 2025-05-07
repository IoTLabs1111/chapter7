# chapter7/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

MONGO_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")

# Optional: for authentication
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# If using auth, you can build the URI like:
# MONGO_URL = f"mongodb://{DB_USER}:{DB_PASSWORD}@localhost:27017/"

client = AsyncIOMotorClient(MONGO_URL)
database = client[DB_NAME]

car_collection = database.get_collection("cars")
