from django.urls import path

from search import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test_celery", views.test_celery, name="test_celery"),
    path("search", views.handle_scrapping, name="search"),
    path("task_status/<str:task_id>", views.check_task_status, name="task_status"),
]
