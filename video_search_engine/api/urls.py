
from django.urls import path
from .views import store_video

urlpatterns = [
    path('upload/', store_video, name='store_video'),
]
