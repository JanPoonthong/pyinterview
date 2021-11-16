from django.utils import timezone

from .models import Upload
import os


def auto_file_deleter():
    for i in Upload.objects.all():
        if i.expire_date < timezone.now():
            os.remove(f"{i.file.name}")
            i.delete()
