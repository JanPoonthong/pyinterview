from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.urls import reverse
from django.db import models

import uuid


class Upload(models.Model):
    file = models.FileField(upload_to="file_uploads/%Y-%m-%d/")
    password = models.CharField(max_length=255, blank=True, null=True)
    max_downloads = models.IntegerField(blank=True, null=True)
    expire_date = models.DateTimeField()
    user_downloads = models.IntegerField(blank=True, null=True, default=0)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )

    def get_absolute_url(self):
        return reverse("download", args=str((self.uuid,)))

    def save(self, *args, **kwargs):
        if self.password is None:
            super(Upload, self).save(*args, **kwargs)
        else:
            self.password = make_password(self.password)
            super(Upload, self).save(*args, **kwargs)
