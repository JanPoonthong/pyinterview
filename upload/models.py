from django.db import models
from django.urls import reverse

import uuid


class Upload(models.Model):
    file = models.FileField(upload_to="file_uploads/%Y-%m-%d/")
    password = models.CharField(max_length=255, blank=True, null=True)
    max_downloads = models.IntegerField(blank=True, null=True)
    expire_date = models.DateTimeField()
    user_downloads = models.IntegerField(blank=True, null=True, default=0)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def get_absolute_url(self):
        return reverse("download", args=str((self.uuid,)))
