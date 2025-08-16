from django.apps import AppConfig
from mongoengine import connect
import os

class VisitorapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitorapi'

    def ready(self):
        try:
            conn = connect(
                host=os.environ.get("MONGODB_URI"),
                db=os.environ.get("MONGODB_DB_NAME")
            )
            print("✅ MongoDB connected:", conn)
        except Exception as e:
            print("❌ MongoDB connection failed:", e)
