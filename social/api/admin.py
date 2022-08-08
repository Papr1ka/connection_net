from django.contrib import admin
from .models import ChatModel, MessageModel, UserModel

# Register your models here.
admin.site.register(UserModel)
admin.site.register(ChatModel)
admin.site.register(MessageModel)