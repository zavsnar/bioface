import jsonfield

from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractUser
 
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
    # form_data = jsonfield.JSONField()
    organism_id = models.CharField(max_length=255)
    display_fields = jsonfield.JSONField()
    attributes_list = jsonfield.JSONField()
    filter_fields = jsonfield.JSONField()



    