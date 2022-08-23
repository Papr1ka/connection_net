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


class UserChatsSerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True)
    class Meta:
        model = UserModel
        fields = ('chats',)


class MessageSerizlizer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = '__all__'



"""class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=150)
    login = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)
    
    def update(self, instanse, validated_data):
        instanse.user_id = validated_data.get("user_id", instanse.user_id)
        instanse.login = validated_data.get("login", instanse.login)
        instanse.password = validated_data.get("password", instanse.password)
        instanse.save()
        return instanse"""