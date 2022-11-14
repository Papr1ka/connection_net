from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class UserModel(models.Model):
    #username, password, email include in user
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    avatar_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    chats = models.ManyToManyField('ChatModel', blank=True)
    status = models.CharField(max_length=200, blank=True)
    display_name = models.CharField(max_length=40, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ChatModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField('UserModel')
    
    def __str__(self):
        return f"{self.id}"


class MessageModel(models.Model):
    chat = models.ForeignKey("ChatModel", on_delete=models.CASCADE, null=True, related_name='messages')
    author_id = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    
    def __str__(self):
        return self.chat_id
