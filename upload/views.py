from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView
from django.urls import reverse
from django.shortcuts import render

import datetime

from .form import UploadForm
from .models import Upload

import mimetypes
import os
import re


class UploadPage(CreateView):
    model = Upload
    form_class = UploadForm

    # TODO:
    # 1) Convert expire_duration to expire_date [_]
    # 2) Upload and save [x]
    # 3) Generate download and delete link [_]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            # TODO(jan): for optional is not ready
            self.password_check(form.cleaned_data["password"])
            expire_duration = int(form.cleaned_data["expire_duration"])
            expire_date = self.convert_duration_to_date(expire_duration)
            upload_model = self.upload_and_save_to_db(form, expire_date)
            return self.check_if_file_size_over(upload_model)

    @staticmethod
    def check_if_file_size_over(upload_model):
        if upload_model == "Over size":
            return HttpResponse("File over 100MB are not allow")
        return HttpResponseRedirect(
            reverse("download", kwargs={"pk": upload_model.id})
        )

    @staticmethod
    def convert_duration_to_date(expire_duration):
        # TODO(jan): DateTime is not correct
        date_and_time = datetime.datetime.now()
        time_change = datetime.timedelta(seconds=expire_duration)
        expire_date = date_and_time + time_change
        return expire_date

    @staticmethod
    def check_file_size(form):
        if not form.file.size >= 104857600:
            form.save()
            return form
        else:
            return "Over size"

    def upload_and_save_to_db(self, form, expire_date):
        # print(form.cleaned_data["file"])
        form = Upload(
            file=form.cleaned_data["file"],
            password=form.cleaned_data["password"],
            max_downloads=form.cleaned_data["max_downloads"],
            expire_date=expire_date,
        )
        return self.check_file_size(form)

    @staticmethod
    def password_check(password):
        """8 characters length or more,
        1 digit or more,
        1 symbol or more,
        1 uppercase letter or more,
        1 lowercase letter or more.
        """
        if password is None:
            return HttpResponseRedirect("24")
        length_error = len(password) < 8
        digit_error = re.search(r"\d", password) is None
        uppercase_error = re.search(r"[A-Z]", password) is None
        lowercase_error = re.search(r"[a-z]", password) is None
        symbol_error = (
            re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
        )
        password_ok = not (
            length_error
            or digit_error
            or uppercase_error
            or lowercase_error
            or symbol_error
        )

        if not password_ok:
            return HttpResponseRedirect(reverse("upload"))
            # return "Password not strong 1 digit or more, 1 symbol or more, 1 uppercase letter or more, 1 lowercase letter or more."
        pass

    def generate_download_and_delete_link(self):
        pass


class Download(DetailView):
    model = Upload

    # TODO:
    # Make it so that you can't download expired files

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.get_upload_file_name(self.object)

        if self.object.password is not None:
            return self.verify_password()
        return self.download_file()

    def verify_password(self):
        if self.request.POST.get("password") != f"{self.object.password}":
            return HttpResponse("invalid password")
        return self.download_file()

    def get_upload_file_name(self, *args, **kwargs):
        file_name = self.object.file.name
        letter = file_name.rsplit("_", 1)
        extension = letter[1].rsplit(".", 1)
        # print(os.path.basename(letter[0]), extension[1])

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
        # return HttpResponse(f"{self.object.file.name} reached the downloads limit")

    def download_file(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = f"{os.path.basename(self.object.file.name)}"
        filepath = base_dir + f"/{self.object.file}"
        path = open(filepath, "rb")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        self.download_counter()
        self.check_max_download()
        return response

        # TODO:
        # 1) Delete file when max_downloads is done [x]
        # 2) Verify password securely [x]
        # 3) Actually send the download [x]


class Delete(DetailView):
    model = Upload
    template_name = "upload/delete.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.delete()
        return HttpResponse("Deleted!")

    def delete(self):
        self.object.delete()
        os.remove(self.object.file.name)
