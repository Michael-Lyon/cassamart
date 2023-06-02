from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from accounts.models import BuyerProfile, SellerProfile
from .models import Messages, Room
from .serializers import MessageSerializer, RoomSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatAPI(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, receiver):
        rooms = None
        messages = None
        data = {}
        sender = request.user
        receiver = User.objects.get(id=receiver)
        if hasattr(sender, "seller"):  # check if the sender is a seller
            # check if a room exists with the seller and buyer
            sender = SellerProfile.objects.get(user=sender)
            receiver = BuyerProfile.objects.get(user=receiver)
            if Room.objects.filter(buyer=receiver, seller=sender).exists():
                rooms = Room.objects.filter(seller=sender)  # get all rooms for the seller
                room = Room.objects.get(buyer=receiver, seller=sender)
                # Get the last 50 messages from the database for the given room_slug
                messages = Messages.objects.filter(room=room).order_by('-date')[:50]
            else:
                room = Room.objects.create(buyer=receiver, seller=sender, name=receiver.username+sender.username)
                data["current_room"] = {"slug": room.slug, "name": room .name}

        elif hasattr(sender, "buyer"):  # check if the sender is a seller
            sender = BuyerProfile.objects.get(user=sender)
            receiver = SellerProfile.objects.get(user=receiver)
            # check if a room exists with the buyer and seller
            if Room.objects.filter(buyer=sender, seller=receiver).exists():
                rooms = Room.objects.filter(buyer=sender)  # gett all rooms for the buyer
                room = Room.objects.get(buyer=sender, seller=receiver)
                # Get the last 50 messages from the database for the given room_slug
                messages = Messages.objects.filter(room=room).order_by('-date')[:50]
                # Serialize the messages & rooms
                message_serializer = MessageSerializer(messages, many=True)
                rooms_serializer = RoomSerializer(rooms, many=True)
                data["messages"] = message_serializer.data
                data["rooms"] = rooms_serializer.data
                data["current_room"] = {"slug": room.slug, "name": room.name}
            else:
                # create a new room if none exists
                room = Room.objects.create(buyer=sender, seller=receiver,
                                           name=receiver.user.username+sender.user.username)
                data["messages"] = "Room created"
                data["current_room"] = {"slug": room.slug, "name": room.name}
        return Response(data)

    def post(self, request, receiver):
        # Create a new message from the request data
        data = request.data
        current_room = data["current_room"]['slug']
        message = data["message"]
        try:
            room = Room.objects.get(slug=current_room)
            message = Messages.objects.create(message=message, room=room, sender=request.user)
            data = MessageSerializer(message)
            # Send the message to the room group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{current_room}',
                {
                    'type': 'chat_message',
                    'message': message.message,
                    'sender': request.user.id,
                    "date": str(message.date)
                }
            )

            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e.with_traceback())
            return Response({"message": e}, status=status.HTTP_400_BAD_REQUEST)
