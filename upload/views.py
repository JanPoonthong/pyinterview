from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView
from django.urls import reverse

from datetime import datetime

from .form import UploadForm
from .models import Upload

import mimetypes
import os
import re


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
            # TODO(jan): for optional is not ready
            self.password_check(form.cleaned_data["password"])
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
    def check_file_size(form):
        if not form.file.size >= 104857600:
            form.save()
            return form
        # return True
        return HttpResponse("File over 100MB are not allow")

    def upload_and_save_to_db(self, form, expire_date):
        # TODO(jan): Check that file is not over 100MB
        form = Upload(
            file=form.cleaned_data["file"],
            password=form.cleaned_data["password"],
            max_downloads=form.cleaned_data["max_downloads"],
            expire_date=expire_date,
        )
        self.check_file_size(form)

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

        if self.object.password is not None:
            return self.verify_password()
        return self.download_file(self.object)

    def verify_password(self):
        if self.request.POST.get("password") != f"{self.object.password}":
            return HttpResponse("invalid password")
        return self.download_file(self.object)

    @staticmethod
    def download_file(current_object):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = f"{os.path.basename(current_object.file.name)}"
        filepath = base_dir + f"/{current_object.file}"
        path = open(filepath, "rb")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

        # TODO:
        # 1) Delete file when max_downloads is done [_]
        # 2) Verify password securely [x]
        # 3) Actually send the download [x]


class Delete(DetailView):
    model = Upload
    template_name = "upload/delete.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        # TODO: Actually delete fil
        self.object.delete()
        return HttpResponse("Deleted!")
