import os


class Config:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/webhook_db")
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
    DATABASE_NAME = "webhook_db"
    COLLECTION_NAME = "events"