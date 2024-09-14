from django.apps import AppConfig
from search.models import ServerStartTimestamp

class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'

    def ready(self):
        # replace with your actual task import
        from search.tasks import search_task
        from django.utils.timezone import now
        from datetime import timedelta

        # Create a new record for the current server start time
        current_time = now()

        # Check if there are any records in the database
        timestamp_records = ServerStartTimestamp.objects.all().order_by('-timestamp')

        if not timestamp_records.exists():
            # No records exist, run the Celery task and save the timestamp
            search_task.delay()  # Run the task asynchronously
            ServerStartTimestamp.objects.create(timestamp=current_time)
        else:
            # Get the most recent timestamp
            last_record = timestamp_records.first()
            last_timestamp = last_record.timestamp

            # Check if the difference between the current time and the last timestamp is more than 15 minutes
            if (current_time - last_timestamp) > timedelta(minutes=15):
                # Difference is more than 15 minutes, run the Celery task and update the timestamp
                search_task.delay()  # Run the task asynchronously
                # Update the last timestamp to the current time
                last_record.timestamp = current_time
                last_record.save()
