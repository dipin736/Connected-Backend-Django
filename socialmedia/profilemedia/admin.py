from django.contrib import admin

from .models import ChatMessage, Post, UserProfile,Comment,Story,StoryImage

# Register your models here.

admin.site.register(UserProfile)

admin.site.register(Post)

admin.site.register(Comment)
admin.site.register(Story)
admin.site.register(StoryImage)
admin.site.register(ChatMessage)




