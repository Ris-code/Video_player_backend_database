from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_id = models.CharField(max_length=200, unique=True, primary_key=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    # class Meta:
    #     db_table = 'video_table'
    #     app_label = 'api'
    #     managed = False


class MyUser(AbstractUser):
    name = models.CharField(max_length=500)
    channel_id = models.CharField(max_length=200, unique=True)
    channel = models.CharField(max_length=200)

#     class Meta:
#         db_table = 'auth_table'
#         app_label = 'api'
#         managed = False
   

