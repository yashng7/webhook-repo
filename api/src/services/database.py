from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.config import Config

_client = None
_db = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_database():
    global _db
    if _db is None:
        client = get_client()
        _db = client[Config.DATABASE_NAME]
    return _db


def check_connection():
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except ConnectionFailure:
        return False


def close_connection():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None