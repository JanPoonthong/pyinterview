from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView
from django.shortcuts import render

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
            expire_duration = int(form.cleaned_data["expire_duration"])
            self.convert_duration_to_date(expire_duration)
            return HttpResponseRedirect("/success/")
        return render(request, self.template_name, self.initial)

    def convert_duration_to_date(self, *args, **kwargs):
        expire_date = datetime.fromtimestamp(*args).strftime(
            "%A, %B %d, %Y %I:%M:%S"
        )
        print(expire_date)

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
