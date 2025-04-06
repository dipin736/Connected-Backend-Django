from rest_framework import serializers
from .models import Post, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    is_following = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'bio', 'hobbies', 'profile_pic', 'cover_photo', 'is_following', 'friends_count']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user in request.user.friends.all()
        return False

    def get_friends_count(self, obj):
        return obj.user.friends.count()


from rest_framework import serializers
from .models import CustomUser, UserProfile

class UserDetailsSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='userprofile.bio', allow_null=True)
    hobbies = serializers.CharField(source='userprofile.hobbies', allow_null=True)
    profile_pic = serializers.ImageField(source='userprofile.profile_pic', allow_null=True)
    cover_photo = serializers.ImageField(source='userprofile.cover_photo', allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'hobbies', 'profile_pic', 'cover_photo']


class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'username', 'profile_pic', 'content', 'image', 'video', 'created_at']

    def get_profile_pic(self, obj):
        profile = getattr(obj.user, 'userprofile', None)
        if profile and profile.profile_pic:
            request = self.context.get('request')
            return request.build_absolute_uri(profile.profile_pic.url)
        return ""
# serializers.py

from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # This will serialize the user as a string (their username)
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment

        fields = ['id', 'user', 'text', 'created_at','profile_pic']
    def get_profile_pic(self, obj):
        profile = getattr(obj.user, 'userprofile', None)
        if profile and profile.profile_pic:
            request = self.context.get('request')
            return request.build_absolute_uri(profile.profile_pic.url)
        return ""
    
from rest_framework import serializers
from .models import Story, StoryImage

class StoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryImage
        fields = ['id', 'image', 'created_at']
    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url
from django.utils.timesince import timesince
from django.utils.timezone import now

class StorySerializer(serializers.ModelSerializer):
    images = StoryImageSerializer(many=True)
    username = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    time_added = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'user', 'username', 'profile_pic', 'images', 'time_added']

    def get_username(self, obj):
        return obj.user.username

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        profile = getattr(obj.user, 'userprofile', None)
        if profile and profile.profile_pic:
            return request.build_absolute_uri(profile.profile_pic.url) if request else profile.profile_pic.url
        return None
    

    def get_time_added(self, obj):
        # Return a "5 minutes ago" style string
        return timesince(obj.time_added, now()) + " ago"

from rest_framework import serializers
from .models import ChatMessage
from accounts.models import CustomUser

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp']

