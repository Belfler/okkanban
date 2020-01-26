from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.timezone import get_default_timezone

from core.models import ChatMessage


class ChatConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.project_pk = None
        self.group_name = None

    def connect(self):
        self.project_pk = self.scope['url_route']['kwargs'].get('project_pk')
        if not self.project_pk:
            self.close()

        self.group_name = f'project_{self.project_pk}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def receive_json(self, content, **kwargs):
        message_text = content['text']
        message_created = ChatMessage.objects.create(
            text=message_text,
            author=self.scope['user'],
            project_id=self.project_pk).created.astimezone(get_default_timezone())
        data = {
            'author': self.scope['user'].get_full_name(),
            'text': message_text,
            'created': naturalday(message_created) + ' at ' + message_created.strftime('%H:%M'),
        }

        async_to_sync(self.channel_layer.group_send)(self.group_name, {
            'type': 'send_message',
            'data': data,
        })

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_message(self, event):
        self.send_json(event['data'])
