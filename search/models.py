# yourapp/models.py
from django.db import models

class ServerStartTimestamp(models.Model):
    # Automatically set timestamp on record creation
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Server started at {self.timestamp}"
