from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime

from .form import UploadForm
from .models import Upload


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
            expire_duration = int(self.cleaned_data(form, "expire_duration"))
            expire_date = self.convert_duration_to_date(expire_duration)
            form = Upload(
                password=self.cleaned_data(form, "password"),
                max_downloads=self.cleaned_data(form, "max_downloads"),
                expire_date=expire_date,
            )
            form.save()
            return HttpResponseRedirect(
                reverse("download", kwargs={"pk": form.id})
            )
        # return render(request, self.template_name, self.initial)

    def cleaned_data(self, form, value):
        return form.cleaned_data[f"{value}"]

    def convert_duration_to_date(self, *args, **kwargs):
        expire_date = datetime.fromtimestamp(*args).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return expire_date

    def upload_and_save_to_db():
        pass

    def generate_download_and_delete_link():
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

        return HttpResponse("todo")

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
