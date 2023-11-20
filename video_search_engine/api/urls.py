
from django.urls import path
from .views import store_video, update_video_data, search_video, upload_video_details, get_video_data, video_suggestion, favorite_video

urlpatterns = [
    path('upload/', store_video, name='store_video'),
    path('update/', update_video_data, name='update_video_data'),
    path('search_video/', search_video, name='search_video'),
    path('get_video_data/<str:video_id>/', get_video_data, name='get_video_data'),
    path('channel/', upload_video_details, name='upload_video_details'),
    path('suggestions/<str:videoID>/', video_suggestion, name='suggestions'),
    path('favorite_video/<str:video_id>/<str:action>/', favorite_video, name='favorite_video'),
]
