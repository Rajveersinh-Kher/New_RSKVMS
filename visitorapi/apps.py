from django.apps import AppConfig
from mongoengine import connect
from django.conf import settings

class VisitorapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitorapi'

    def ready(self):
        if not hasattr(self, "mongo_connected"):
            try:
                connect(**settings.MONGODB_SETTINGS)
                self.mongo_connected = True
                print("✅ MongoDB connected to:", settings.MONGODB_SETTINGS["db"])
            except Exception as e:
                print("❌ MongoDB connection failed:", e)
