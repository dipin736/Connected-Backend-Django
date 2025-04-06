
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .searializers import ChatMessageSerializer, CommentSerializer, PostSerializer, StorySerializer, UserDetailsSerializer, UserProfileSerializer
from .models import Post, UserProfile,Comment
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from accounts.models import Friendship

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)  # Get user by user_id
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

        # If profile doesn't exist, create a blank one
    profile, created = UserProfile.objects.get_or_create(user=user)

    serializer = UserProfileSerializer(profile, context={'request': request})
    return Response(serializer.data)


# View to get and update profile
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user  # Get the logged-in user

    try:
        profile = UserProfile.objects.get(user=user)  # Get the user's profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)  # If profile doesn't exist, create it
        profile.save()

    # Update the profile data with the data from the request
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  # Save the updated profile
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Optional: remove if public
def get_all_users(request):
    users = CustomUser.objects.all()

    # Ensure every user has a profile
    from .models import UserProfile
    for user in users:
        UserProfile.objects.get_or_create(user=user)

    serializer = UserDetailsSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_friends(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

    friendships = Friendship.objects.filter(from_user=user).select_related('to_user')

    data = []
    for relation in friendships:
        friend = relation.to_user
        profile = UserProfile.objects.filter(user=friend).first()
        profile_pic_url = (
            request.build_absolute_uri(profile.profile_pic.url)
            if profile and profile.profile_pic
            else ""
        )
        mutual_count = friend.friends.filter(id__in=request.user.friends.all()).count()

        data.append({
            "id": friend.id,
            "name": friend.username,
            "profilePic": profile_pic_url,
            "isFollowing": friend in request.user.friends.all(),
            "mutualFriends": mutual_count,
            "addedAt": relation.created_at.isoformat(),  # ✅ used for "Recently added"
        })

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = PostSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

    posts = Post.objects.filter(user=user).order_by('-created_at')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, user=request.user)
        post.delete()
        return Response({"detail": "Post deleted successfully."}, status=204)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_posts(request):
    # Get all posts, ordered by creation time
    posts = Post.objects.all().order_by('-created_at')
    
    # Serialize the posts
    serializer = PostSerializer(posts, many=True, context={'request': request})
    
    # Return the serialized posts without pagination
    return Response(serializer.data)

# Like a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)  # Unlike the post
        else:
            post.likes.add(user)  # Like the post
        post.save()
        return Response({"likes_count": post.likes.count()}, status=200)  # Return the updated like count
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_liked(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        is_liked = request.user in post.likes.all()
        return Response({"is_liked": is_liked}, status=200)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)


# Comment on a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comment_text = request.data.get('comment', '')
        if not comment_text:
            return Response({"detail": "Comment cannot be empty."}, status=400)

        comment = Comment.objects.create(post=post, user=request.user, text=comment_text)
        post.comments.add(comment)
        post.save()
        return Response({"comments": post.comments.count()}, status=200)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)
    
# views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_like_count(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        return Response({"likes_count": post.likes.count()}, status=200)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)

# views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comment_count(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        return Response({"comments_count": post.comments.count()}, status=200)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comments = post.comments.all()  # Fetch comments for the post
        # Serialize the comments
        comment_serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(comment_serializer.data, status=200)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found."}, status=404)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Story, StoryImage

from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_story(request):
    user = request.user
    # Parse incoming files (images)
    if 'images' not in request.FILES:
        return Response({"error": "No images provided"}, status=400)

    images = request.FILES.getlist('images')  # Get images from request
    story = Story.objects.create(user=user)  # Create a new story instance
    
    # Save images associated with the story
    for img in images:
        story_image = StoryImage.objects.create(image=img)
        story.images.add(story_image)
    
    # Serialize the story object and return response
    return Response({"message": "Story created successfully", "story_id": story.id}, status=201)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Story


@api_view(['GET'])
def get_stories(request):
    stories = Story.objects.all().order_by('-time_added')
    serializer = StorySerializer(stories, many=True, context={"request": request})  # ✅ Add context
    return Response(serializer.data)

# from datetime import timedelta
# from django.utils.timezone import now

# @api_view(['GET'])
# def get_stories(request):
#     twenty_four_hours_ago = now() - timedelta(hours=24)
#     stories = Story.objects.filter(time_added__gte=twenty_four_hours_ago).order_by('-time_added')
#     serializer = StorySerializer(stories, many=True, context={"request": request})
#     return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatMessage
from accounts.models import CustomUser


class ChatHistoryView(APIView):
    def get(self, request, user1, user2):
        messages = ChatMessage.objects.filter(
            sender_id__in=[user1, user2],
            receiver_id__in=[user1, user2]
        ).order_by('timestamp')
        return Response(ChatMessageSerializer(messages, many=True).data)

# views.py
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser

@api_view(['GET'])
def get_online_users(request):
    online_user_ids = cache.get("online_users", set())
    print(f"[API] ✅ Returning online users: {online_user_ids}")

    users = CustomUser.objects.filter(id__in=online_user_ids).select_related('userprofile')

    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile_pic': request.build_absolute_uri(user.userprofile.profile_pic.url) if user.userprofile and user.userprofile.profile_pic else None
        })

    return Response(user_data)