from django.shortcuts import render
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatModel, MessageModel, UserModel
from .serializers import ChatSerializer, MessageSerizlizer, UserChatsSerializer, UserModelSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

# Create your views here.

class UserAPIView(generics.ListAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserModelSerializer
    permission_classes = (IsAuthenticated, )
    
    def perform_create(self, serializer):
        user=self.request.user
        serializer.save(user=user)


class UserChatsAPIView(generics.ListCreateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserChatsSerializer
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        usermodel = UserModel.objects.get(id=request.user.id)
        if usermodel:
            return Response({'chats': UserChatsSerializer(usermodel).data})
        return Response({'error': 'Object does not exists'})

class ChatAPIView(generics.CreateAPIView):
    queryset = ChatModel.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        if request.data['users'][0] == str(request.user.id):
            return Response({'error': 'Invalid user list'})
        print(request.data)
        print(type(request.data))
        #a = ChatModel.objects.filter(users__iexact=[request.data['users'][0], request.user.id]).first()
        a = ChatModel.objects.filter(users__in=[request.data['users'][0]]).distinct().filter(users__in=[str(request.user.id)]).distinct()
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

        return Response({'message': serializer.data})
        
    


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