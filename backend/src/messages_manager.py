import queue
from typing import List
from models.model import Message
        
class ChannelMessagesSubscriber:
    def __init__(self):
        self.queue = queue.Queue()

    def update(self, message: Message):
        self.queue.put(message)
        
    def retrieve_update(self) -> Message:
        return self.queue.get()


class ChannelMessagesObserver:
    def __init__(self):
        self.subscribers: List[ChannelMessagesSubscriber] = []


    def add_listener(self, subscriber: ChannelMessagesSubscriber = None):
        if subscriber is None:
            subscriber = ChannelMessagesSubscriber()
        self.subscribers.append(subscriber)
        return subscriber


    def publish_message(self, message: Message):
        for subscriber in self.subscribers:
            subscriber.update(message)

    def publish(self, id, author_id, channel_id, content, timestamp, ):
        message = Message(id, content, author_id, timestamp, channel_id)
        self.publish_message(message)