from django.urls import path
from search import views

urlpatterns = [
    path("", views.index, name="index"),
    path("task_status/<str:task_id>", views.check_task_status, name="task_status"),
]
