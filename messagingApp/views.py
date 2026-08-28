
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accountsApp.models import User
from parentsApp.models import Parent
from studentsApp.models import Student

from .forms import ParentMessageForm
from .models import Message, UserTypingStatus


logger = logging.getLogger(__name__)


# ==========================================================
# HELPERS
# ==========================================================


def display_user_name(user):
    """
    Return the user's full name when available.
    Otherwise fall back to the username.
    """

    return (
        user.get_full_name().strip()
        or user.username
    )


def conversation_queryset(user, other):
    """
    Return all messages exchanged between two users.
    """

    return (
        Message.objects
        .filter(
            Q(
                sender=user,
                recipient=other,
            )
            |
            Q(
                sender=other,
                recipient=user,
            )
        )
        .select_related(
            "sender",
            "recipient",
        )
        .order_by("created_at", "id")
    )


def mark_conversation_read(user, other):
    """
    Mark messages received by the current user as read.
    """

    return Message.objects.filter(
        sender=other,
        recipient=user,
        is_read=False,
    ).update(
        is_read=True,
    )


def get_teacher_parent_users(user):
    """
    Return parents belonging to pupils in the teacher's
    assigned classes.

    This is deliberately restricted to the teacher's classes.
    """

    if not hasattr(user, "teacher"):
        return User.objects.none()

    teacher = user.teacher

    assigned_classes = teacher.assigned_class.all()

    parent_ids = (
        Student.objects
        .filter(
            class_room__in=assigned_classes,
            parent__isnull=False,
        )
        .values_list(
            "parent_id",
            flat=True,
        )
        .distinct()
    )

    return (
        User.objects
        .filter(
            parent__id__in=parent_ids,
            role="parent",
            is_active=True,
        )
        .exclude(
            id=user.id,
        )
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )


def get_allowed_message_recipients(user):
    """
    Build the users that the current account can select when
    composing a new message.

    Pupil accounts are deliberately excluded from the current
    general compose screen.

    The application uses:
        pupil
    NOT:
        student
    """

    # ------------------------------------------------------
    # ADMIN USERS
    # ------------------------------------------------------

    admin_users = (
        User.objects
        .filter(
            Q(is_staff=True)
            | Q(is_superuser=True),
            is_active=True,
        )
        .exclude(
            id=user.id,
        )
        .exclude(
            role="pupil",
        )
        .distinct()
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )

    # ------------------------------------------------------
    # TEACHERS
    # ------------------------------------------------------

    teacher_users = (
        User.objects
        .filter(
            role="teacher",
            is_active=True,
        )
        .exclude(
            id=user.id,
        )
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )

    # ------------------------------------------------------
    # PARENTS
    # ------------------------------------------------------

    parent_users = get_teacher_parent_users(user)

    # ------------------------------------------------------
    # PARENTS CAN MESSAGE STAFF / TEACHERS
    # ------------------------------------------------------

    if user.role == "parent":

        teacher_users = (
            User.objects
            .filter(
                role="teacher",
                is_active=True,
            )
            .exclude(
                id=user.id,
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        parent_users = User.objects.none()

    # ------------------------------------------------------
    # PUPILS
    # ------------------------------------------------------

    if user.role == "pupil":

        teacher_users = (
            User.objects
            .filter(
                role="teacher",
                is_active=True,
            )
            .exclude(
                id=user.id,
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )

        parent_users = User.objects.none()

    return {
        "admin_users": admin_users,
        "teacher_users": teacher_users,
        "parent_users": parent_users,
    }


# ==========================================================
# USER INBOX
# ==========================================================


@login_required
def user_inbox(request):
    """
    Display all conversations belonging to the logged-in user.

    A conversation is represented by the other participant and
    the latest message exchanged with that participant.
    """

    user = request.user

    messages_qs = (
        Message.objects
        .filter(
            Q(sender=user)
            |
            Q(recipient=user)
        )
        .select_related(
            "sender",
            "recipient",
        )
        .order_by(
            "-created_at",
            "-id",
        )
    )

    conversations = {}

    for msg in messages_qs:

        if msg.sender_id == user.id:
            other = msg.recipient
        else:
            other = msg.sender

        if other is None:
            continue

        if other.id not in conversations:

            conversations[other.id] = {
                "user": other,
                "last_message": msg,
                "unread_count": 0,
            }

        if (
            msg.recipient_id == user.id
            and not msg.is_read
        ):

            conversations[
                other.id
            ]["unread_count"] += 1

    conversation_list = list(
        conversations.values()
    )

    context = {
        "conversations": conversation_list,
        "total_unread": sum(
            conversation["unread_count"]
            for conversation in conversation_list
        ),
    }

    return render(
        request,
        "messagingApp/inbox.html",
        context,
    )


# ==========================================================
# CONVERSATION
# ==========================================================


@login_required
def conversation(request, user_id):

    user = request.user

    other = get_object_or_404(
        User,
        id=user_id,
        is_active=True,
    )

    if user.id == other.id:

        messages.error(
            request,
            "You cannot message yourself.",
        )

        return redirect("inbox")

    # ------------------------------------------------------
    # Mark incoming messages as read
    # ------------------------------------------------------

    mark_conversation_read(
        user,
        other,
    )

    # ------------------------------------------------------
    # Send message from normal conversation form
    # ------------------------------------------------------

    if request.method == "POST":

        body = (
            request.POST.get(
                "body",
                "",
            )
            .strip()
        )

        if not body:

            messages.error(
                request,
                "Message cannot be empty.",
            )

        else:

            Message.objects.create(
                sender=user,
                recipient=other,
                subject=(
                    f"Conversation with "
                    f"{display_user_name(other)}"
                ),
                message_type="other",
                body=body,
            )

            messages.success(
                request,
                "Message sent successfully.",
            )

            return redirect(
                "conversation",
                user_id=other.id,
            )

    messages_qs = conversation_queryset(
        user,
        other,
    )

    context = {
        "other": other,
        "messages": messages_qs,
        "current_user": user,
    }

    return render(
        request,
        "messagingApp/conversation.html",
        context,
    )


# ==========================================================
# PARENT -> ADMIN MESSAGE
# ==========================================================


@login_required
def parent_send_message(request):

    if request.user.role != "parent":

        messages.error(
            request,
            "Only parent accounts can use this form.",
        )

        return redirect("inbox")

    if request.method == "POST":

        form = ParentMessageForm(
            request.POST,
        )

        if form.is_valid():

            msg = form.save(
                commit=False,
            )

            msg.sender = request.user

            admin_user = (
                User.objects
                .filter(
                    is_superuser=True,
                    is_active=True,
                )
                .first()
            )

            if admin_user is None:

                admin_user = (
                    User.objects
                    .filter(
                        is_staff=True,
                        is_active=True,
                    )
                    .exclude(
                        id=request.user.id,
                    )
                    .first()
                )

            if admin_user is None:

                messages.error(
                    request,
                    "No active administrator is available.",
                )

            else:

                msg.recipient = admin_user

                msg.save()

                messages.success(
                    request,
                    "Your message has been sent.",
                )

                return redirect(
                    "conversation",
                    user_id=admin_user.id,
                )

        else:

            messages.error(
                request,
                "Please correct the errors below.",
            )

    else:

        form = ParentMessageForm()

    sent_messages = (
        Message.objects
        .filter(
            sender=request.user,
        )
        .select_related(
            "recipient",
        )
        .order_by(
            "-created_at",
            "-id",
        )[:10]
    )

    context = {
        "form": form,
        "sent_messages": sent_messages,
    }

    return render(
        request,
        "messagingApp/parent_message_form.html",
        context,
    )


# ==========================================================
# ADMIN INBOX
# ==========================================================


@login_required
def admin_message_list(request):

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        messages.error(
            request,
            "Permission denied.",
        )

        return redirect("home")

    messages_qs = (
        Message.objects
        .filter(
            recipient=request.user,
        )
        .select_related(
            "sender",
            "recipient",
        )
        .order_by(
            "-created_at",
            "-id",
        )
    )

    conversations = {}

    for msg in messages_qs:

        sender = msg.sender

        if sender is None:
            continue

        if sender.id not in conversations:

            conversations[sender.id] = {
                "user": sender,
                "last_message": msg,
                "unread_count": 0,
            }

        if not msg.is_read:

            conversations[
                sender.id
            ]["unread_count"] += 1

    conversation_list = list(
        conversations.values()
    )

    context = {
        "conversations": conversation_list,
        "unread_count": sum(
            item["unread_count"]
            for item in conversation_list
        ),
    }

    return render(
        request,
        "messagingApp/admin_messages.html",
        context,
    )


# ==========================================================
# ADMIN MESSAGE DETAIL
# ==========================================================


@login_required
def admin_message_detail(request, pk):

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        messages.error(
            request,
            "Permission denied.",
        )

        return redirect("home")

    msg = get_object_or_404(
        Message.objects.select_related(
            "sender",
            "recipient",
        ),
        pk=pk,
    )

    # ------------------------------------------------------
    # Only mark it read if the logged-in admin is the
    # recipient.
    # ------------------------------------------------------

    if msg.recipient_id == request.user.id:

        Message.objects.filter(
            pk=msg.pk,
            is_read=False,
        ).update(
            is_read=True,
        )

    return redirect(
        "conversation",
        user_id=msg.sender_id,
    )


# ==========================================================
# RECENT MESSAGE API
# ==========================================================


@login_required
def get_recent_messages(request):

    messages_qs = (
        Message.objects
        .filter(
            recipient=request.user,
        )
        .select_related(
            "sender",
        )
        .order_by(
            "-created_at",
            "-id",
        )[:5]
    )

    data = []

    for msg in messages_qs:

        typing_status = (
            UserTypingStatus.objects
            .filter(
                user=msg.sender,
            )
            .first()
        )

        is_typing = (
            typing_status.is_typing
            if typing_status
            else False
        )

        data.append(
            {
                "id": msg.id,
                "subject": msg.subject,
                "body": msg.body[:60],
                "type": msg.get_message_type_display(),
                "sender_id": msg.sender_id,
                "sender_name": display_user_name(
                    msg.sender
                ),
                "created_at": msg.created_at.strftime(
                    "%d %b %Y, %H:%M"
                ),
                "is_read": msg.is_read,
                "is_typing": is_typing,
            }
        )

    return JsonResponse(
        {
            "messages": data,
        }
    )


# ==========================================================
# CONVERSATION API
# ==========================================================


@login_required
def get_conversation_api(
    request,
    user_id,
):

    user = request.user

    other = get_object_or_404(
        User,
        id=user_id,
        is_active=True,
    )

    mark_conversation_read(
        user,
        other,
    )

    messages_qs = conversation_queryset(
        user,
        other,
    )

    typing_status = (
        UserTypingStatus.objects
        .filter(
            user=other,
        )
        .first()
    )

    is_other_typing = (
        typing_status.is_typing
        if typing_status
        else False
    )

    data = []

    for msg in messages_qs:

        data.append(
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": display_user_name(
                    msg.sender
                ),
                "body": msg.body,
                "created_at": msg.created_at.strftime(
                    "%H:%M, %d %b %Y"
                ),
                "is_self": (
                    msg.sender_id == user.id
                ),
                "is_read": msg.is_read,
            }
        )

    return JsonResponse(
        {
            "messages": data,
            "other_typing": is_other_typing,
        }
    )


# ==========================================================
# SEND MESSAGE API
# ==========================================================


@login_required
def send_message_api(
    request,
    user_id,
):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required",
            },
            status=400,
        )

    try:

        data = json.loads(
            request.body.decode(
                "utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "error": "Invalid JSON",
            },
            status=400,
        )

    body = (
        data.get(
            "body",
            "",
        )
        .strip()
    )

    if not body:

        return JsonResponse(
            {
                "error": "Empty message",
            },
            status=400,
        )

    other = get_object_or_404(
        User,
        id=user_id,
        is_active=True,
    )

    if other.id == request.user.id:

        return JsonResponse(
            {
                "error": "You cannot message yourself.",
            },
            status=400,
        )

    msg = Message.objects.create(
        sender=request.user,
        recipient=other,
        subject=(
            f"Conversation with "
            f"{display_user_name(other)}"
        ),
        message_type="other",
        body=body,
    )

    return JsonResponse(
        {
            "status": "ok",
            "message": {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "sender_name": display_user_name(
                    msg.sender
                ),
                "body": msg.body,
                "created_at": msg.created_at.strftime(
                    "%H:%M, %d %b %Y"
                ),
                "is_self": True,
                "is_read": msg.is_read,
            },
        }
    )


# ==========================================================
# TYPING INDICATOR
# ==========================================================


@login_required
def typing_indicator(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required",
            },
            status=400,
        )

    try:

        data = json.loads(
            request.body.decode(
                "utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "error": "Invalid JSON",
            },
            status=400,
        )

    is_typing = bool(
        data.get(
            "is_typing",
            False,
        )
    )

    status, created = (
        UserTypingStatus.objects
        .get_or_create(
            user=request.user,
        )
    )

    status.is_typing = is_typing

    status.save(
        update_fields=[
            "is_typing",
        ]
    )

    return JsonResponse(
        {
            "status": "ok",
        }
    )


# ==========================================================
# DELETE MESSAGE
# ==========================================================


@login_required
def delete_message(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required",
            },
            status=400,
        )

    try:

        data = json.loads(
            request.body.decode(
                "utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse(
            {
                "error": "Invalid JSON",
            },
            status=400,
        )

    message_id = data.get(
        "message_id"
    )

    if not message_id:

        return JsonResponse(
            {
                "error": "Message ID required",
            },
            status=400,
        )

    msg = get_object_or_404(
        Message,
        id=message_id,
    )

    if (
        msg.sender_id != request.user.id
        and not (
            request.user.is_staff
            or request.user.is_superuser
        )
    ):

        return JsonResponse(
            {
                "error": "Permission denied",
            },
            status=403,
        )

    msg.delete()

    return JsonResponse(
        {
            "status": "ok",
        }
    )


# ==========================================================
# CLEAR CONVERSATION
# ==========================================================


@login_required
def clear_conversation_api(
    request,
    user_id,
):

    if not (
        request.user.is_staff
        or request.user.is_superuser
    ):

        return JsonResponse(
            {
                "error": (
                    "Permission denied. "
                    "Only administrators can "
                    "clear conversations."
                ),
            },
            status=403,
        )

    if request.method != "POST":

        return JsonResponse(
            {
                "error": "POST required",
            },
            status=400,
        )

    other = get_object_or_404(
        User,
        id=user_id,
    )

    messages_to_delete = Message.objects.filter(
        Q(
            sender=request.user,
            recipient=other,
        )
        |
        Q(
            sender=other,
            recipient=request.user,
        )
    )

    count = messages_to_delete.count()

    messages_to_delete.delete()

    return JsonResponse(
        {
            "status": "ok",
            "deleted_count": count,
        }
    )


# ==========================================================
# SEND MESSAGE TO ANY USER
# ==========================================================


@login_required
def send_message_to_any(request):

    if request.method == "POST":

        recipient_id = request.POST.get(
            "recipient"
        )

        subject = (
            request.POST.get(
                "subject",
                "",
            )
            .strip()
        )

        body = (
            request.POST.get(
                "body",
                "",
            )
            .strip()
        )

        if not recipient_id:

            messages.error(
                request,
                "Please select a recipient.",
            )

            return redirect(
                "send_message_to_any"
            )

        if not subject:

            messages.error(
                request,
                "Please enter a subject.",
            )

            return redirect(
                "send_message_to_any"
            )

        if not body:

            messages.error(
                request,
                "Please enter a message.",
            )

            return redirect(
                "send_message_to_any"
            )

        recipient = get_object_or_404(
            User,
            id=recipient_id,
            is_active=True,
        )

        if recipient.id == request.user.id:

            messages.error(
                request,
                "You cannot send a message to yourself.",
            )

            return redirect(
                "send_message_to_any"
            )

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body,
            message_type="other",
        )

        messages.success(
            request,
            (
                "Message sent to "
                f"{display_user_name(recipient)}."
            ),
        )

        return redirect(
            "inbox"
        )

    recipient_groups = (
        get_allowed_message_recipients(
            request.user
        )
    )

    context = {
        **recipient_groups,
    }

    return render(
        request,
        "messagingApp/compose_message.html",
        context,
    )
