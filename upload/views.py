from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime

from .form import UploadForm
from .models import Upload

import mimetypes
import os


class UploadPage(CreateView):
    model = Upload
    form_class = UploadForm

    # TODO:
    # 1) Convert expire_duration to expire_date
    # 2) Upload and save
    # 3) Generate download and delete link

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            print(dir(form.cleaned_data["file"]))
            expire_duration = int(form.cleaned_data["expire_duration"])
            expire_date = self.convert_duration_to_date(expire_duration)
            upload_model = self.upload_and_save_to_db(form, expire_date)
            return HttpResponseRedirect(
                reverse("download", kwargs={"pk": upload_model.id})
            )

    @staticmethod
    def convert_duration_to_date(expire_duration):
        # TODO(jan): DateTime is not correct
        expire_date = datetime.fromtimestamp(expire_duration).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return expire_date

    @staticmethod
    def upload_and_save_to_db(form, expire_date):
        # TODO(jan): Check that file is not over 100MB
        form = Upload(
            file=form.cleaned_data["file"],
            password=form.cleaned_data["password"],
            max_downloads=form.cleaned_data["max_downloads"],
            expire_date=expire_date,
        )
        form.save()
        return form

    def generate_download_and_delete_link(self):
        pass


class Download(DetailView):
    model = Upload

    # TODO:
    # Make it so that you can't download expired files

    def post(self, *args, **kwargs):
        self.object = self.get_object()

        if self.object.password is not None:
            if self.request.POST.get("password") != "password":
                return HttpResponse("invalid password")

        return self.download_file(self.object)
        # return HttpResponse(f"{self.object.file}")
        # return HttpResponse("todo")

    @staticmethod
    def download_file(current_object):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = f"{os.path.basename(current_object.file.name)}"
        filepath = BASE_DIR + f"/{current_object.file}"
        path = open(filepath, "rb")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

        # TODO:
        # 1) Delete file when max_downloads is done
        # 2) Verify password securely
        # 3) Actually send the download


class Delete(DetailView):
    model = Upload
    template_name = "upload/delete.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        # TODO: Actually delete fil
        self.object.delete()
        return HttpResponse("Deleted!")
