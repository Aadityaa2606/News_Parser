from search.tasks import search_task
from django.http import HttpResponse, JsonResponse


def index(request):
    return JsonResponse({"status": "OK"})


def handle_scrapping(request):
    query = request.GET.get("query")
    task1 = search_task.delay(query)
    return JsonResponse({"task_id": task1.id})


def check_task_status(request, task_id):
    result = search_task.AsyncResult(task_id, app=search_task.backend)
    response = {
        "status": result.status,
        "result": result.result,
    }
    return JsonResponse(response)
