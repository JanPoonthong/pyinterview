from django.utils import timezone

from .models import Upload
import os


def auto_file_deleter():
    for i in Upload.objects.all():
        if timezone.localtime(i.expire_date) < timezone.localtime(
            timezone.now()
        ):
            # os.remove(f"{i.file.name}")
            return i.delete()
        else:
            return f"Nothing was Delete"
