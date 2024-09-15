# yourapp/models.py
from django.db import models

class ServerStartTimestamp(models.Model):
    # Automatically set timestamp on record creation
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Server started at {self.timestamp}"
    

class UserAPIRequest(models.Model):
    user_id = models.IntegerField(unique=True)
    request_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user_id} - Requests: {self.request_count}"
