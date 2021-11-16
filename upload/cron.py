from django.utils import timezone

from .models import Upload


def auto_file_deleter():
    for i in Upload.objects.all():
        if timezone.localtime(i.expire_date) < timezone.localtime(
            timezone.now()
        ):
            return i.delete()
