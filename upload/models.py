from django.db import models
from django.urls import reverse


class Upload(models.Model):
    file = models.FileField(upload_to="file_uploads/%Y-%m-%d/")
    password = models.CharField(max_length=255, blank=True, null=True)
    max_downloads = models.IntegerField()
    expire_date = models.DateTimeField()
    # TODO: Add more fields if needed

    def get_absolute_url(self):
        return reverse("download", args=(self.id,))
