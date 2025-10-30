import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import BoardingRecord


class consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'cards_monitor'


        await self.channel_layer.group_add(
            self.room_group_name,   
            self.channel_name
        ) 
        
        await self.accept()
        print("consumers.py---cliente conectado")

    
    async def disconnect(self, close_code):
        self.channel_layer.group_discard(
            self.room_group_name,   
            self.channel_name
        )
        print("consumers.py---cliente desconectado")


    async def send_event(self, event):
        await self.send(text_data=json.dumps(event['event'], ensure_ascii=False))