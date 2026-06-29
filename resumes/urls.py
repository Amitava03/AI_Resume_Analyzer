from django.urls import path

from . import views

app_name = "resumes"

urlpatterns = [
    path("", views.resume_list, name="list"),
    path("upload/", views.resume_upload, name="upload"),
    path("<int:pk>/", views.resume_detail, name="detail"),
    path("<int:pk>/match/", views.job_match, name="job_match"),
]
