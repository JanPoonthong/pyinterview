from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.views import View

from send.settings import LOGIN_URL
from .form import UploadForm
from .models import Upload

import mimetypes
import datetime
import os


class UploadPage(CreateView):
    model = Upload
    form_class = UploadForm

    # TODO:
    # 1) Convert expire_duration to expire_date [x]
    # 2) Upload and save [x]
    # 3) Generate download and delete link [x]

    @method_decorator(login_required(login_url=LOGIN_URL))
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            expire_duration = int(form.cleaned_data["expire_duration"])
            expire_date = self.convert_duration_to_date(expire_duration)
            upload_model = self.upload_and_save_to_db(form, expire_date)
            return self.check_if_file_size_over(upload_model)

    @staticmethod
    def check_if_file_size_over(upload_model):
        if upload_model == "Over size":
            return HttpResponse("File over 100MB are not allow")
        return HttpResponseRedirect(
            reverse("download", kwargs={"uuid": upload_model.uuid})
        )

    @staticmethod
    def convert_duration_to_date(expire_duration):
        expire_date = timezone.localtime(timezone.now()) + timezone.timedelta(
            seconds=expire_duration
        )
        return expire_date

    @staticmethod
    def check_file_size(form):
        if not form.file.size >= 104857600:
            form.save()
            return form
        else:
            return "Over size"

    def upload_and_save_to_db(self, form, expire_date):
        form = self.model(
            file=form.cleaned_data["file"],
            password=form.cleaned_data["password"],
            max_downloads=form.cleaned_data["max_downloads"],
            expire_date=expire_date,
            owner=self.request.user,
        )
        return self.check_file_size(form)


class Download(DetailView):
    model = Upload

    # TODO:
    # Make it so that you can't download expired files

    def get_object(self, queryset=None):
        return self.model.objects.get(uuid=self.kwargs.get("uuid"))

    @method_decorator(login_required(login_url=LOGIN_URL))
    def post(self, *args, **kwargs):
        self.object = self.get_object()

        if self.object.password is not None:
            return self.verify_password()
        return self.download_file()

    def verify_password(self):
        if not check_password(
            self.request.POST.get("password"), self.object.password
        ):
            return HttpResponse("invalid password")
        return self.download_file()

    def download_counter(self):
        counter = self.object
        counter.user_downloads = int(counter.user_downloads) + 1
        counter.save()

    def check_max_download(self):
        if self.object.max_downloads == self.object.user_downloads:
            self.delete()

    def delete(self):
        self.object.delete()
        os.remove(self.object.file.name)

    @staticmethod
    def checking_file_type(filename, filepath):
        path = open(filepath, "rb")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

    def getting_file_dir(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = f"{os.path.basename(self.object.file.name)}"
        filepath = base_dir + f"/{self.object.file}"
        return filename, filepath

    def download_file(self):
        filename, filepath = self.getting_file_dir()
        response = self.checking_file_type(filename, filepath)
        self.download_counter()
        self.check_max_download()
        return response

        # TODO:
        # 1) Delete file when max_downloads is done [x]
        # 2) Verify password securely [x]
        # 3) Actually send the download [x]


class Logout(View):
    @method_decorator(login_required(login_url=LOGIN_URL))
    def get(self, *args, **kwargs):
        logout(self.request)
        return HttpResponse("Your account has been logout")


class Login(View):
    template_name = "upload/login.html"

    def get(self, *args, **kwargs):
        return self.check_if_user_authenticated()

    def check_if_user_authenticated(self):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("upload"))
        return render(self.request, self.template_name, {})

    def post(self, *args, **kwargs):
        username = self.request.POST["username"]
        password = self.request.POST["password"]
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
        else:
            return HttpResponse("Invalid username and/or password")
        return HttpResponseRedirect(reverse("upload"))


class Register(View):
    template_name = "upload/register.html"

    def get(self, *args, **kwargs):
        return self.check_if_user_authenticated()

    def check_if_user_authenticated(self):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("upload"))
        return render(self.request, self.template_name, {})

    def post(self, *args, **kwargs):
        username = self.request.POST["username"]
        password = self.request.POST["password"]
        confirmation = self.request.POST["confirmation"]
        return self.username_and_password_checker(
            username, password, confirmation
        )

    @staticmethod
    def username_and_password_checker(username, password, confirmation):
        if password != confirmation:
            return HttpResponse("Passwords must match")
        try:
            user = User.objects.create_user(
                username=username, password=password
            )
            user.save()
        except ValueError:
            return HttpResponse("Fill up the form")
        except IntegrityError:
            return HttpResponse("Username already taken")
        return HttpResponseRedirect("login")


class Delete(DetailView):
    model = Upload
    template_name = "upload/delete.html"

    def get_object(self, queryset=None):
        return self.model.objects.get(uuid=self.kwargs.get("uuid"))

    @method_decorator(login_required(login_url=LOGIN_URL))
    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return self.check_owner_of_file()

    def check_owner_of_file(self):
        if self.request.user == self.object.owner:
            self.delete()
            return HttpResponse("Deleted!")
        return HttpResponse(
            f"You can't not delete, only <strong>User: {self.object.owner}</strong> can delete this file"
        )

    def delete(self):
        self.object.delete()
        os.remove(self.object.file.name)
