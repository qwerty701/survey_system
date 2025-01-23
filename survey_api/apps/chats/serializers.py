from rest_framework import serializers

from .models import ChatRoom, Message


class ChatSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = ChatRoom
        fields = ["id", "users", "survey"]


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ["id", "chatroom", "sender", "content"]
