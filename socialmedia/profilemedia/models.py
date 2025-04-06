from django.db import models
from accounts.models import CustomUser
from django.db.models import CASCADE
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    cover_photo = models.ImageField(upload_to="cover_photos/", blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField('Comment', related_name='post_comments', blank=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.user.username}'s post"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments_on_post', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='user_comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"



from django.db import models

class Story(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stories')  # User who created the story
    images = models.ManyToManyField('StoryImage', related_name='stories')  # Related images for the story
    time_added = models.DateTimeField(auto_now_add=True)  # Time when the story was added
    
    def __str__(self):
        return f"Story by {self.user.username} added on {self.time_added}"

class StoryImage(models.Model):
    image = models.ImageField(upload_to='stories/images/')  # Image file
    created_at = models.DateTimeField(auto_now_add=True)  # When the image was uploaded

    def __str__(self):
        return f"Image created on {self.created_at}"


class ChatMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
