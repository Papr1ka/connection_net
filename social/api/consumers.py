
import json

from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer

from .models import ChatModel, MessageModel
from .serializers import MessageSerizlizer, UserChatsIdSerializer
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
    
    @database_sync_to_async
    def get_chat(self, pk: int) -> Union[ChatModel, None]:
        try:
            chat = ChatModel.objects.get(pk=pk)
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
