
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import GroupMembership, GroupMessage, Message


User = get_user_model()


# ==========================================================
# DIRECT MESSAGE DATABASE FUNCTIONS
# ==========================================================

@database_sync_to_async
def fetch_recent_direct(user_id, other_id, limit=50, before=None):
    queryset = Message.objects.filter(
        Q(sender_id=user_id, receiver_id=other_id)
        | Q(sender_id=other_id, receiver_id=user_id)
    ).select_related(
        "sender"
    ).order_by(
        "-id"
    )

    if before:
        queryset = queryset.filter(id__lt=before)

    messages = list(queryset[:limit])

    data = []

    for message in reversed(messages):
        data.append(
            {
                "id": message.id,
                "sender_id": message.sender_id,
                "sender_name": (
                    message.sender.get_full_name()
                    or message.sender.username
                ),
                "sender_has_photo": bool(
                    message.sender.profile_photo
                ),
                "sender_photo_url": (
                    message.sender.profile_photo.url
                    if message.sender.profile_photo
                    else None
                ),
                "content": message.content,
                "file_url": (
                    message.file.url
                    if message.file
                    else None
                ),
                "timestamp": message.timestamp.isoformat(),
            }
        )

    return data


@database_sync_to_async
def fetch_direct_message(message_id):
    message = Message.objects.select_related(
        "sender"
    ).get(
        id=message_id
    )

    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "sender_name": (
            message.sender.get_full_name()
            or message.sender.username
        ),
        "sender_has_photo": bool(
            message.sender.profile_photo
        ),
        "sender_photo_url": (
            message.sender.profile_photo.url
            if message.sender.profile_photo
            else None
        ),
        "content": message.content,
        "file_url": (
            message.file.url
            if message.file
            else None
        ),
        "timestamp": message.timestamp.isoformat(),
    }


@database_sync_to_async
def create_direct_message(sender_id, other_id, content):
    message = Message.objects.create(
        sender_id=sender_id,
        receiver_id=other_id,
        content=content,
    )

    return message.id


@database_sync_to_async
def user_exists(user_id):
    return User.objects.filter(
        id=user_id
    ).exists()


# ==========================================================
# GROUP MESSAGE DATABASE FUNCTIONS
# ==========================================================

@database_sync_to_async
def fetch_recent_group(group_id, limit=50, before=None):
    queryset = GroupMessage.objects.filter(
        group_id=group_id
    ).select_related(
        "sender"
    ).order_by(
        "-id"
    )

    if before:
        queryset = queryset.filter(id__lt=before)

    messages = list(queryset[:limit])

    data = []

    for message in reversed(messages):
        data.append(
            {
                "id": message.id,
                "sender_id": message.sender_id,
                "sender_name": (
                    message.sender.get_full_name()
                    or message.sender.username
                ),
                "sender_has_photo": bool(
                    message.sender.profile_photo
                ),
                "sender_photo_url": (
                    message.sender.profile_photo.url
                    if message.sender.profile_photo
                    else None
                ),
                "content": message.content,
                "file_url": (
                    message.file.url
                    if message.file
                    else None
                ),
                "timestamp": message.timestamp.isoformat(),
            }
        )

    return data


@database_sync_to_async
def fetch_group_message(message_id):
    message = GroupMessage.objects.select_related(
        "sender"
    ).get(
        id=message_id
    )

    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "sender_name": (
            message.sender.get_full_name()
            or message.sender.username
        ),
        "sender_has_photo": bool(
            message.sender.profile_photo
        ),
        "sender_photo_url": (
            message.sender.profile_photo.url
            if message.sender.profile_photo
            else None
        ),
        "content": message.content,
        "file_url": (
            message.file.url
            if message.file
            else None
        ),
        "timestamp": message.timestamp.isoformat(),
    }


@database_sync_to_async
def create_group_message(group_id, sender_id, content):
    message = GroupMessage.objects.create(
        group_id=group_id,
        sender_id=sender_id,
        content=content,
    )

    return message.id


@database_sync_to_async
def group_membership_exists(group_id, user_id):
    return GroupMembership.objects.filter(
        group_id=group_id,
        user_id=user_id,
    ).exists()


# ==========================================================
# DIRECT CHAT CONSUMER
# ==========================================================

class DirectChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.room_name = None

        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.other_id = int(
            self.scope["url_route"]["kwargs"]["user_id"]
        )

        if not await user_exists(self.other_id):
            await self.close()
            return

        try:
            other_user = await database_sync_to_async(
                User.objects.get
            )(
                id=self.other_id
            )

        except User.DoesNotExist:
            await self.close()
            return

        allowed = False

        if (
            user.role == "admin"
            and other_user.role in ["teacher", "parent"]
        ):
            allowed = True

        elif (
            user.role == "teacher"
            and other_user.role in ["parent", "admin"]
        ):
            allowed = True

        elif (
            user.role == "parent"
            and other_user.role in ["teacher", "admin"]
        ):
            allowed = True

        if not allowed:
            await self.close()
            return

        first_id = min(
            user.id,
            self.other_id,
        )

        second_id = max(
            user.id,
            self.other_id,
        )

        self.room_name = (
            f"direct_{first_id}_{second_id}"
        )

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name,
        )

        await self.accept()

        recent_messages = await fetch_recent_direct(
            user.id,
            self.other_id,
        )

        await self.send_json(
            {
                "type": "init",
                "messages": recent_messages,
            }
        )


    async def receive_json(
        self,
        content,
        **kwargs,
    ):

        action = content.get("action")

        if action == "send":

            text = content.get(
                "content",
                "",
            ).strip()

            if text:

                message_id = await create_direct_message(
                    self.scope["user"].id,
                    self.other_id,
                    text,
                )

                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        "type": "broadcast.message",
                        "message_id": message_id,
                    }
                )


        elif action == "load_older":

            before = content.get("before")

            older_messages = await fetch_recent_direct(
                self.scope["user"].id,
                self.other_id,
                before=before,
            )

            await self.send_json(
                {
                    "type": "older",
                    "messages": older_messages,
                }
            )


        elif action == "typing":

            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "typing.event",
                    "user_id": self.scope["user"].id,
                }
            )


    async def broadcast_message(
        self,
        event,
    ):

        try:

            message = await fetch_direct_message(
                event["message_id"]
            )

            await self.send_json(
                {
                    "type": "new",
                    "message": message,
                }
            )

        except Message.DoesNotExist:
            return


    async def typing_event(
        self,
        event,
    ):

        if (
            event["user_id"]
            != self.scope["user"].id
        ):

            await self.send_json(
                {
                    "type": "typing",
                    "user_id": event["user_id"],
                }
            )


    async def external_message(
        self,
        event,
    ):

        await self.send_json(
            {
                "type": "new",
                "message": event["message"],
            }
        )


    async def external_reaction(
        self,
        event,
    ):

        await self.send_json(
            {
                "type": "reaction",
                "message_id": event["message_id"],
                "reactions": event["reactions"],
            }
        )


    async def disconnect(
        self,
        close_code,
    ):

        if self.room_name:

            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name,
            )


# ==========================================================
# GROUP CHAT CONSUMER
# ==========================================================

class GroupChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.room_name = None

        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.group_id = int(
            self.scope["url_route"]["kwargs"]["group_id"]
        )

        is_member = await group_membership_exists(
            self.group_id,
            user.id,
        )

        if not is_member:
            await self.close()
            return

        self.room_name = (
            f"group_{self.group_id}"
        )

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name,
        )

        await self.accept()

        recent_messages = await fetch_recent_group(
            self.group_id
        )

        await self.send_json(
            {
                "type": "init",
                "messages": recent_messages,
            }
        )


    async def receive_json(
        self,
        content,
        **kwargs,
    ):

        action = content.get("action")

        if action == "send":

            text = content.get(
                "content",
                "",
            ).strip()

            if text:

                message_id = await create_group_message(
                    self.group_id,
                    self.scope["user"].id,
                    text,
                )

                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        "type": "broadcast.message",
                        "message_id": message_id,
                    }
                )


        elif action == "load_older":

            before = content.get("before")

            older_messages = await fetch_recent_group(
                self.group_id,
                before=before,
            )

            await self.send_json(
                {
                    "type": "older",
                    "messages": older_messages,
                }
            )


        elif action == "typing":

            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "typing.event",
                    "user_id": self.scope["user"].id,
                }
            )


    async def broadcast_message(
        self,
        event,
    ):

        try:

            message = await fetch_group_message(
                event["message_id"]
            )

            await self.send_json(
                {
                    "type": "new",
                    "message": message,
                }
            )

        except GroupMessage.DoesNotExist:
            return


    async def typing_event(
        self,
        event,
    ):

        if (
            event["user_id"]
            != self.scope["user"].id
        ):

            await self.send_json(
                {
                    "type": "typing",
                    "user_id": event["user_id"],
                }
            )


    async def external_message(
        self,
        event,
    ):

        await self.send_json(
            {
                "type": "new",
                "message": event["message"],
            }
        )


    async def external_reaction(
        self,
        event,
    ):

        await self.send_json(
            {
                "type": "reaction",
                "message_id": event["message_id"],
                "reactions": event["reactions"],
            }
        )


    async def disconnect(
        self,
        close_code,
    ):

        if self.room_name:

            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name,
            )
