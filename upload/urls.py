from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadPage.as_view(), name="upload"),
    path("<uuid:uuid>", views.Download.as_view(), name="download"),
    path("delete/<uuid:uuid>", views.Delete.as_view(), name="delete"),
    path("register", views.Register.as_view(), name="register"),
    path("login", views.Login.as_view(), name="login"),
    path("logout", views.Logout.as_view(), name="logout"),
]
