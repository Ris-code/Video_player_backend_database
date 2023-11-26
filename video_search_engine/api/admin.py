from django.contrib import admin
from .models import  Video, MyUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User 

# admin.site.unregister(User)
# Register the Video model
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_id', 'likes', 'dislikes', 'views')

# # Register the MyUser model
@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'channel_id', 'channel', 'email', 'is_active')
    search_fields = ('username', 'name', 'channel_id', 'channel', 'email')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)
# admin.site.register(MyUser)