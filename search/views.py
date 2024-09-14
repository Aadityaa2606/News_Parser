from search.tasks import hello_world, search_task
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from doc_retrival.celery import app


def index(request):
    return JsonResponse({"status": "OK"})


def test_celery(request):
    hello_world.delay()  # Call the task asynchronously
    return HttpResponse("Task has been triggered!")


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
