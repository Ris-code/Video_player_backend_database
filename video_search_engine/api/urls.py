
from django.urls import path
from .views import store_video, update_video_data, search_video, upload_video_details, get_video_data, createpost, login_user, playlist, check_like, check_playlist, frontpage, get_history, history_view, get_likes, get_playlist, like_view, playlist_view, get_uploaded_videos, uploaded_video_details, video_suggestion

urlpatterns = [
    path('', frontpage, name='frontpage'),
    path('upload/', store_video, name='store_video'),
    path('update/', update_video_data, name='update_video_data'),
    path('search_video/', search_video, name='search_video'),
    path('get_video_data/<str:video_id>/', get_video_data, name='get_video_data'),
    path('channel/', upload_video_details, name='upload_video_details'),
    path('suggestions/<str:videoID>/', video_suggestion, name='suggestions'),
    path('signup/', createpost, name='signup'),
    path('login/', login_user, name='login'),
    path('playlist/<str:video_id>/<str:action>/', playlist, name='playlist'),
    path('check_like/<str:video_id>/', check_like, name='already_liked'),
    path('check_playlist/<str:video_id>/', check_playlist, name='already_playlisted'),
    path('get_history/<str:username>/', get_history, name='get_history'),
    path('get_likes/<str:username>/', get_likes, name='get_like'),
    path('get_playlist/<str:username>/', get_playlist, name='get_playlist'),
    path('get_uploaded_videos/<str:username>/', get_uploaded_videos, name='get_playlist'),
    path('history/', history_view, name='history'),
    path('likes/', like_view, name='like'),
    path('playlist/', playlist_view, name='playlist'),
    path('uploaded_videos/', uploaded_video_details, name='upload_video_details')
    # path('json/', home, name='home')
]
