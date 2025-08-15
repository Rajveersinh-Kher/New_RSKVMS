from django.apps import AppConfig
from mongoengine import connect
import os

class VisitorapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitorapi'

    def ready(self):
        connect(
            host=os.environ.get("MONGODB_URI"),
            db=os.environ.get("MONGODB_DB_NAME")
        )
