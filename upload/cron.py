from django.utils import timezone

from .models import Upload
import os


def auto_file_deleter():
    for i in Upload.objects.all():
        if i.expire_date < timezone.now():
            i.delete()
            os.remove(i.file.name)
