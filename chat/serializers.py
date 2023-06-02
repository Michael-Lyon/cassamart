from rest_framework import serializers
from .models import Room, Messages


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'slug')


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Messages
        fields = ('id', 'message', 'date', 'sender', 'room', 'read')


class RoomInlineSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    buyer = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    # detail_edit_url = serializers.HyperlinkedIdentityField(
    #     view_name="chat:chat_api",
    #     receiver=
    # )
