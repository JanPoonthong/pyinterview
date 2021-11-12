from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadPage.as_view(), name="upload"),
    path("<slug:pk>", views.Download.as_view(), name="download"),
    path("delete/<slug:pk>", views.Delete.as_view(), name="delete"),
]
