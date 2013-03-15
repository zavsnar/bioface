import jsonfield

from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractUser

ENCODING_CHOUCES = (('utf-8', 'utf-8'), ('cp1251','cp1251'))

class CustomUser(AbstractUser):
    # username = models.CharField(max_length=40, unique=True, db_index=True)
    # email = models.EmailField(max_length=254, unique=True)
    sessionkey = models.CharField(max_length=255, blank=True)
 
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username']

# class CustomUser(models.Model):

# 	user = models.OneToOneField(User, related_name='profile')
# 	sessionkey = models.CharField(max_length=255, blank=True)

class SavedQuery(models.Model):
    type_query = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(CustomUser, related_name='saved_queries')
    created = models.DateTimeField(auto_now=True, auto_now_add=True)
    # form_data = jsonfield.JSONField()
    organism_id = models.CharField(max_length=255)
    display_fields = jsonfield.JSONField()
    attributes_list = jsonfield.JSONField()
    filter_fields = jsonfield.JSONField()

class Download(models.Model):
    user = models.ForeignKey(CustomUser, related_name='downloads')
    file = models.FileField(upload_to='downloads', null=True)
    encoding = models.ChoiceField(choices=ENCODING_CHOUCES, default='utf-8')
    description = models.TextField()
    status = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    