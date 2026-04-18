import queue
from typing import List, Dict

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


class ServerMembersSubscriber:
    def __init__(self):
        self.queue = queue.Queue()

    def update(self, member: dict):
        self.queue.put(member)

    def retrieve_update(self) -> dict:
        return self.queue.get()


class ServerMembersObserver:
    def __init__(self):
        self.subscribers: List[ServerMembersSubscriber] = []

    def add_listener(self, subscriber: ServerMembersSubscriber = None):
        if subscriber is None:
            subscriber = ServerMembersSubscriber()
        self.subscribers.append(subscriber)
        return subscriber

    def publish_member(self, member: dict):
        for subscriber in self.subscribers:
            subscriber.update(member)

    def publish(self, id: str, server_id: str, username: str):
        member = {"id": id, "server_id": server_id, "username": username}
        self.publish_member(member)


server_members_observers: Dict[str, ServerMembersObserver] = {}
