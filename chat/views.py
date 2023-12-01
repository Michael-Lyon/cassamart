from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.models import Profile

from .models import Messages, Room
from .serializers import MessageSerializer, RoomSerializer

User = get_user_model()

class ChatAPI(APIView):
    """
        API endpoint for managing chat functionality between buyers and sellers.

        Authentication:
        - The request should include a valid JWT token in the Authorization header.

        GET Request:
        - Retrieves chat data between the authenticated user and the specified receiver.
        - The receiver ID should be provided as a URL parameter. If receiver ID is None, returns a list of rooms that the current user is a part of.
        - Returns the list of rooms and messages associated with the chat.

        POST Request:
        - Sends a message from the authenticated user to the specified receiver.
        - The receiver ID should be provided as a URL parameter.
        - The request body should include the current_room slug and the message content.
        - Returns the serialized message if successful.

        Note:
        - The sender's role (buyer or seller) is determined based on the authenticated user.
        - The receiver can be either a buyer or a seller depending on the sender's role.

        Example Usage:
        GET Request:
        GET /chat/123/

        POST Request:
        POST /chat/123/
        {
            "current_room": {
                "slug": "room-slug"
            },
            "message": "Hello, this is a test message."
        }
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_receiver_profile(self, receiver_id):
        """
        Retrieve the profile of the receiver based on the provided receiver ID.
        Return the profile if found, or raise a 404 error.
        """
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)
            try:
                profile = Profile.objects.get(user=receiver)
                return profile
            except ObjectDoesNotExist:
                return None
        else:
            return None

    def get_rooms_and_messages(self, sender_profile, receiver_profile, sender_role):
        """
        Retrieve the rooms and messages between the sender and receiver.
        Return the rooms and messages.
        """
        rooms = None
        messages = None
        room = None

        if sender_role == "buyer":
            rooms = Room.objects.filter(buyer=sender_profile)
            if receiver_profile:
                room = Room.objects.filter(
                    buyer=sender_profile, seller=receiver_profile.user).first()
        elif sender_role == "seller":
            rooms = Room.objects.filter(seller=sender_profile)
            if receiver_profile:
                room = Room.objects.filter(
                    buyer=receiver_profile.user, seller=sender_profile).first()

        if room:
            messages = Messages.objects.filter(room=room).order_by('date')[:50]
        else:
            if receiver_profile:
                room = Room.objects.create(
                    buyer=sender_profile if sender_role == "buyer" else receiver_profile.user,
                    seller=sender_profile if sender_role == "seller" else receiver_profile.user,
                    name=f"{sender_profile.user.username}-{receiver_profile.user.username}"
                )

        return rooms, messages, room

    def get(self, request, receiver_id):
        sender_profile = request.user.profile
        receiver_profile = self.get_receiver_profile(
            receiver_id) if receiver_id else None

        sender_role = "seller" if sender_profile.is_seller else "buyer"

        rooms, messages, current_room = self.get_rooms_and_messages(
            sender_profile, receiver_profile, sender_role)

        room_serializer = RoomSerializer(rooms, many=True)
        if messages:
            message_serializer = MessageSerializer(messages, many=True)
        else:
            message_serializer = None

        data = {
            "rooms": room_serializer.data,
            "messages": message_serializer.data,
            "current_room": {"slug": current_room.slug, "name": current_room.name} if current_room else None
        }
        return Response(data)

    def post(self, request, receiver_id):
        data = request.data
        current_room_slug = data["current_room"]["slug"]
        message_content = data["message"]

        try:
            room = Room.objects.get(slug=current_room_slug)
            message = Messages.objects.create(
                message=message_content, room=room, sender=request.user)
            message_serializer = MessageSerializer(message)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{current_room_slug}',
                {
                    'type': 'chat_message',
                    'message': message.message,
                    'sender': request.user.id,
                    'date': str(message.date)
                }
            )

            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        except Room.DoesNotExist:
            return Response({"errors": "Room does not exist.", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"errors": str(e), "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
