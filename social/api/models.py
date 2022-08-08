from django.db import models
from django.contrib.auth.models import User

class UserModel(models.Model):
    #username, password, email include in user
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    chats = models.ManyToManyField('ChatModel', blank=True)
    
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(self.chats, self.chats.count())


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
