from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=255)
    friends = models.ManyToManyField("self",through="Friendship",symmetrical=False, blank=True, related_name='followers')
    def __str__(self):
        return self.username

class Friendship(models.Model):
    from_user = models.ForeignKey('CustomUser', related_name='from_users', on_delete=models.CASCADE)
    to_user = models.ForeignKey('CustomUser', related_name='to_users', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)