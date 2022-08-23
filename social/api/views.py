from email import message
from django.shortcuts import render
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatModel, MessageModel, UserModel
from .serializers import ChatSerializer, MessageSerizlizer, UserChatsSerializer, UserDjangoSerizlizer, UserModelSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

# Create your views here.

class UserListAPIView(generics.ListAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = (IsAuthenticated, )
    
    def perform_create(self, serializer):
        user=self.request.user
        serializer.save(user=user)


class UserApiView(generics.RetrieveUpdateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserModelSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'put', 'head']
    
    def get(self, request):
        usermodel = UserModel.objects.get(id=request.user.id)
        return Response(UserModelSerializer(usermodel).data)
    
    def put(self, request):
        new_username = request.data.get('username', None)
        if new_username:
            user_exist = User.objects.filter(username=new_username).exists()
            if user_exist:
                return Response({'error': 'User with this username is alredy exists'})
            else:
                instance = User.objects.get(pk=request.user.pk)
                
                serializer = UserDjangoSerizlizer(instance=instance, data={'username': new_username})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                return Response({'put': serializer.data})
        
        new_avatar = request.data.get('avatar', None)
        if new_avatar:
            instance = self.queryset.get(pk=request.user.pk)
            instance.avatar_image = new_avatar
            instance.save()
            return Response({'put': UserModelSerializer(instance).data})
        return Response({'statuscode': '200'})


class UserChatsAPIView(generics.ListCreateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserChatsSerializer
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        usermodel = UserModel.objects.get(id=request.user.id)
        if usermodel:
            new_chats = {'chats': []}
            chats = UserChatsSerializer(usermodel).data
            
            for i in chats['chats']:
                messages_length = len(i['messages'])
                if messages_length > 0:
                    msg = MessageModel.objects.get(id=i['messages'][-1])
                    #msg = serializers.serialize('json', [ msg, ])
                    msg = MessageSerizlizer(msg)
                    last_message = [msg.data]
                else:
                    last_message = []
                users = i['users']
                users.remove(request.user.id)
                user = UserModel.objects.get(id=users[0])
                contact_username = user.user.username
                if user.avatar_image:
                    avatar = user.avatar_image.url
                else:
                    avatar = None
                new_chats['chats'].append({
                    'id': i['id'],
                    'messages': [] if messages_length == 0 else i['messages'][:min(50, messages_length)],
                    'created_at': i['created_at'],
                    'users': [{'id': users[0], 'username': contact_username, 'avatar_image': avatar}],
                    'last_message': last_message,
                })
            
            return Response({'chats': new_chats})
        return Response({'error': 'Object does not exists'})


class ChatAPIView(generics.CreateAPIView):
    queryset = ChatModel.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        if request.data['users'] == str(request.user.id):
            return Response({'error': 'Invalid user list'})
        #a = ChatModel.objects.filter(users__iexact=[request.data['users'][0], request.user.id]).first()
        a = ChatModel.objects.filter(users__in=[request.data['users']]).distinct().filter(users__in=[str(request.user.id)]).distinct()
        if a:
            return Response({'error': 'Chat alredy exists'})
        
        data = request.data.copy()
        data.appendlist('users', str(request.user.id))
        serializer = ChatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        r = serializer.save()
        user = UserModel.objects.get(id=request.user.id)
        user.chats.add(r)
        user2 = UserModel.objects.get(id=request.data['users'][0])
        user2.chats.add(r)
        
        return Response({'post': serializer.data})


class MessageAPIView(generics.ListCreateAPIView):
    queryset = MessageModel.objects.all()
    serializer_class = MessageSerizlizer
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        channel = request.data.get("chat_id", None)
        part = request.data.get("part", None)
        if not channel:
            return Response({'error': 'Expected chat_id'})
        if not part:
            return Response({'error': 'Expected part'})
        try:
            part = int(part)
        except:
            return Response({'error': 'Expected part:int'})
        
        try:
            channel = ChatModel.objects.get(id=channel)
        except ChatModel.DoesNotExist:
            return Response({'error': 'Invalid chat_id'})
        
        access = False
        for i in channel.users.values():
            if i['id'] == request.user.id:
                access = True
                break
        
        if not access:
            return Response({'error': 'Access blocked'})
        
        count_messages = channel.messages.count()
        start = max(count_messages - 20 * part, 0)
        end = max(count_messages - 20 * (part - 1), 0)

        return Response({'messages': MessageSerizlizer(channel.messages.all()[start:end], many=True).data})
    
    def post(self, request):
        channel = request.data.get("chat_id", None)
        if not channel:
            return Response({'error': 'Expected chat_id'})
        text = request.data.get("text", None)
        if not text or text == '':
            return Response({'error': 'Expected text'})
        
        try:
            channel = ChatModel.objects.get(id=channel)
        except ChatModel.DoesNotExist:
            return Response({'error': 'Invalid chat_id'})
        
        access = False
        for i in channel.users.values():
            if i['id'] == request.user.id:
                access = True
                break
        
        if not access:
            return Response({'error': 'Access blocked'})
        
        data = {
            "chat": request.data["chat_id"],
            "author_id": request.user.id,
            "text": text
        }
        
        serializer = MessageSerizlizer(data=data)
        serializer.is_valid(raise_exception=True)
        r = serializer.save()

        return Response(serializer.data)
        
    


"""class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        return Response({'users': UserSerializer(users, many=True).data})
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({'post': serializer.data})
    
    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method PUT is not allowed"})
        
        try:
            instanse = User.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        serializer = UserSerializer(data=request.data, instance=instanse)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data})"""