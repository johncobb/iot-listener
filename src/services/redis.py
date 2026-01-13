import redis
import json
from datetime import datetime

class RedisQueue:

    def __init__(self, queue_name='messages', host='localhost', port=6379, db=0):
        """initialize redis connection"""
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.queue_name = queue_name

    def enqueue(self, message):
        """add a message to the queue"""
        # message_data = {
        #     'content': message,
        #     'timestamp': datetime.now().isoformat()
        # }
        # self.redis_client.rpush(self.queue_name, json.dumps(message_data))
        self.redis_client.rpush(self.queue_name, message)

    def dequeue(self):
        """remove and return a message from the queue"""
        message = self.redis_client.lpop(self.queue_name)
        if message:
            message_data = json.loads(message)
            return message_data
        else:
            return None

    def peek(self):
        """view the next message without removing it"""
        message = self.redis_client.lindex(self.queue_name, 0)
        if message:
            message_data = json.loads(message)
            return message_data
        return None

    def size(self):
        """get the number of messages in the queue"""
        return self.redis_client.llen(self.queue_name)

    def clear(self):
        """clear all messages from the queue"""
        self.redis_client.delete(self.queue_name)
