from search.tasks import search_task
from django.http import JsonResponse, HttpResponseForbidden
from search.utils import retrieve_from_chromadb
from datetime import timedelta
from search.models import UserAPIRequest
from django.utils.timezone import now
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('django')


def index(request):
    # Start time for inference
    start_time = datetime.now()

    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse({"error": "user_id is required"}, status=400)

    # Ensure user_id is an integer
    try:
        user_id = int(user_id)
    except ValueError:
        return JsonResponse({"error": "user_id must be an integer"}, status=400)

    # Check the request limit
    limit = 5
    time_limit = timedelta(minutes=5)  # 5-minute window

    # Get or create the user entry
    user_entry, created = UserAPIRequest.objects.get_or_create(user_id=user_id)

    if not created:
        # Check if the user exceeded the request limit
        if (now() - user_entry.last_request_time) < time_limit:
            if user_entry.request_count >= limit:
                return HttpResponseForbidden("Too many requests. Try again later.", status=429)
            else:
                user_entry.request_count += 1
                user_entry.save()
        else:
            # Reset count after the time limit
            user_entry.request_count = 1
            user_entry.save()
    else:
        # New user entry
        user_entry.request_count = 1
        user_entry.save()

    query = request.GET.get("text", "business")
    top_k = int(request.GET.get("top_k", 10))
    threshold = request.GET.get("threshold")
    threshold = float(threshold) if threshold else None

    results = retrieve_from_chromadb(
        query=query, top_k=top_k, threshold=threshold)

    # Calculate inference time
    inference_time = (datetime.now() - start_time).total_seconds()

    # Log the request and inference time
    logger.info(f'User ID: {user_id}, Query: {query}, Top_k: {top_k}, Threshold: {threshold}, Inference Time: {inference_time}s')

    # Add inference time to the response
    response = JsonResponse(results)
    response['X-Inference-Time'] = inference_time
    return response

def check_task_status(request, task_id):
    result = search_task.AsyncResult(task_id, app=search_task.backend)
    response = {
        "status": result.status,
        "result": result.result,
    }
    return JsonResponse(response)
