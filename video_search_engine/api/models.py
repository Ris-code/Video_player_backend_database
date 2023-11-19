from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_id = models.CharField(max_length=200, unique=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    
   

