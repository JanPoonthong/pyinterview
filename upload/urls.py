from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadPage.as_view(), name="upload"),
    path("<uuid:uuid>", views.Download.as_view(), name="download"),
    path("delete/<uuid:uuid>", views.Delete.as_view(), name="delete"),
]
