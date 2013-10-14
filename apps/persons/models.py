import jsonfield

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from settings import DOWNLOADS_ROOT, DOWNLOADS_URL

ENCODING_CHOUCES = (('utf-8', 'utf-8'), ('cp1251','cp1251'), ('MacCyrillic', 'MacCyrillic'))

class CustomUser(AbstractUser):
    # Session key in API
    sessionkey = models.CharField(max_length=255, blank=True)
 
    USERNAME_FIELD = 'username'

class SavedQuery(models.Model):
    type_query = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(CustomUser, related_name='saved_queries')
    created = models.DateTimeField(auto_now=True, auto_now_add=True)
    organism_id = models.CharField(max_length=255)
    display_fields = jsonfield.JSONField()
    attributes_list = jsonfield.JSONField()
    filter_fields = jsonfield.JSONField()
    query_str = models.TextField()
    paginate_by = models.IntegerField(default=10)
    sort_by = models.CharField(max_length=255, null=True)

class Download(models.Model):
    user = models.ForeignKey(CustomUser, related_name='downloads')
    file_path = models.FilePathField(path=DOWNLOADS_ROOT, match="*.zip", recursive=True, null=True)
    encoding = models.CharField(choices=ENCODING_CHOUCES, max_length="255", default='utf-8')
    description = models.TextField(null=True)
    status = models.CharField(max_length=255)
    task_id = models.CharField(max_length="255")
    created = models.DateTimeField(auto_now_add=True)

    def download_url(self):
        return DOWNLOADS_URL + self.file_path
