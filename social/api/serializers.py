from rest_framework import serializers
from .models import ChatModel, MessageModel, UserModel, User

class UserDjangoSerizlizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'date_joined', 'id')


class UserModelSerializer(serializers.ModelSerializer):
    user = UserDjangoSerizlizer()
    class Meta:
        model = UserModel
        fields = ('id', 'user', 'avatar_image')


class ChatSerializer(serializers.ModelSerializer):
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = ChatModel
        fields = '__all__'

class ChatIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatModel
        fields = ('id',)


class UserChatsSerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True)
    class Meta:
        model = UserModel
        fields = ('chats',)


class UserChatsIdSerializer(serializers.ModelSerializer):
    chats = ChatIdSerializer(many=True)
    class Meta:
        model = UserModel
        fields = ('chats',)
    


class MessageSerizlizer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = '__all__'
