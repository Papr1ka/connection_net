
import json

from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer

from .models import ChatModel, MessageModel, UserModel
from .serializers import AllUserSerializer, ChatSerializer, MessageSerizlizer, UserChatsIdSerializer, UserChatsSerializer
from django.contrib.auth.models import AnonymousUser

from typing import Union


class MessageConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = MessageModel.objects.all()
    serializer_class = MessageSerizlizer
    
    @action()
    async def start_listen(self, **kwargs):
        """
        Событие, вызываемое пользователем при намерении начать прослушивать все касающиеся его события
        """
        
        #список id чатов, в которых состоит пользователь
        user_chats = await self.get_user_chats(self.scope['user'])
        for i in user_chats:
            i = i['id']
            await self.subscribe_to_messages_in_chat(i)
        await self.subscribe_to_new_chat()
    
    @database_sync_to_async
    def get_chat(self, pk: int) -> Union[ChatModel, None]:
        try:
            chat = ChatModel.objects.get(pk=pk)
            return chat
        except ChatModel.DoesNotExist:
            return None
    
    @database_sync_to_async
    def is_user_in_chat(self, chat) -> bool:
        for i in chat.users.values():
            if i['id'] == self.scope['user'].id:
                return True
        return False
    
    
    @action()
    async def create_message(self, chat_id, text, **kwargs):
        chat: ChatModel = await self.get_chat(pk=chat_id)
        if not chat:
            await self.send(text_data=json.dumps({'error': "Chat does not exists"}))
        else:
            access = await self.is_user_in_chat(chat)
            if not access:
                await self.send(text_data=json.dumps({'error': "Access blocked"}))
            else:
                await database_sync_to_async(MessageModel.objects.create)(
                    chat=chat,
                    author_id=self.scope["user"].id,
                    text=text
                )

    @database_sync_to_async
    def get_user_chats(self, user):
        """
        Принимает: django User с полем account | AnonymousUser
        Возвращает: List[OrderedDict([('id', int)]] | []
        """
        if isinstance(user, AnonymousUser):
            return []
        else:
            user_model = UserChatsIdSerializer(user.account).data
            return user_model['chats']
    
    async def subscribe_to_messages_in_chat(self, pk):
        print(self.scope['user'], "subscribed to", pk)
        """
        Подписаться на оповещения об изменении Chat.messages с id = pk
        """
        await self.message_activity.subscribe(chat=pk)
    
    @model_observer(MessageModel)
    async def message_activity(self, message, observer=None, **kwargs):
        print('message', message)
        """
        Отправка события изменения конкретного сообщения всем подписанным на это пользователям
        """
        message['event'] = "on_message_create"
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: MessageModel, **kwargs):
        yield f'chat__{instance.chat_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, chat=None, **kwargs):
        if chat is not None:
            yield f'chat__{chat}'

    @message_activity.serializer
    def message_activity(self, instance: MessageModel, action, **kwargs) -> dict:
        return dict(data=MessageSerizlizer(instance).data, action=action.value, pk=instance.pk)

    
    async def subscribe_to_new_chat(self):
        print(self.scope['user'], "subscribed to self")
        """
        Подписаться на оповещения об изменении Chat.messages с id = pk
        """
        print(self.scope['user'].pk)
        await self.chat_activity.subscribe(user=self.scope['user'].pk)
    
    
    
    @model_observer(UserModel)
    async def chat_activity(self, chat, observer=None, **kwargs):
        print('chat', chat)
        """
        Отправка события создания чата всем подписанным на это пользователям
        """
        chat['event'] = "on_user_state_change"
        try:
            await self.subscribe_to_messages_in_chat(chat['data']['chats'][-1]['id'])
        except IndexError:
            print("new user can't be resolved")
        
        await self.send_json(chat)

    @chat_activity.groups_for_signal
    def chat_activity(self, instance: UserModel, **kwargs):
        yield f'pk__{instance.pk}'

    @chat_activity.groups_for_consumer
    def chat_activity(self, user=None, **kwargs):
        if user is not None:
            yield f'pk__{user}'

    @chat_activity.serializer
    def chat_activity(self, instance: UserModel, action, **kwargs) -> dict:
        return dict(data=AllUserSerializer(instance).data, action=action.value, pk=instance.pk)
