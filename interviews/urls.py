from django.urls import path

from . import views

app_name = "interviews"

urlpatterns = [
    path("", views.session_list, name="list"),
    path("create/", views.session_create, name="create"),
    path("<int:pk>/", views.session_detail, name="session_detail"),
    path("questions/<int:pk>/answer/", views.answer_question, name="answer"),
]
