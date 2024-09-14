from celery import shared_task
from search.utils import search

@shared_task
def hello_world():
    print("Hello, World!")

@shared_task
def search_task(query):
    return search(query)
