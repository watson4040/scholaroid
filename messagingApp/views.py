from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Message, UserTypingStatus
from .forms import ParentMessageForm
from accountsApp.models import User
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def user_inbox(request):
    user = request.user
    messages_qs = Message.objects.filter(Q(sender=user) | Q(recipient=user)).select_related('sender', 'recipient')
    conversations = {}
    for msg in messages_qs.order_by('-created_at'):
        other = msg.recipient if msg.sender == user else msg.sender
        if other:
            if other.id not in conversations:
                conversations[other.id] = {'user': other, 'last_message': msg, 'unread_count': 0}
            if msg.recipient == user and not msg.is_read:
                conversations[other.id]['unread_count'] += 1
    return render(request, 'messagingApp/inbox.html', {'conversations': conversations.values()})

@login_required
def conversation(request, user_id):
    other = get_object_or_404(User, id=user_id)
    user = request.user
    if user == other:
        messages.error(request, "You cannot message yourself.")
        return redirect('inbox')
    Message.objects.filter(sender=other, recipient=user, is_read=False).update(is_read=True)
    messages_qs = Message.objects.filter(
        (Q(sender=user, recipient=other) | Q(sender=other, recipient=user))
    ).order_by('created_at')
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            msg = Message.objects.create(
                sender=user,
                recipient=other,
                subject=f"Re: Conversation with {other.get_full_name() or other.username}",
                message_type='other',
                body=body,
            )
            messages.success(request, "Message sent.")
            return redirect('conversation', user_id=other.id)
        else:
            messages.error(request, "Message cannot be empty.")
    return render(request, 'messagingApp/conversation.html', {'other': other, 'messages': messages_qs})

@login_required
def parent_send_message(request):
    if request.method == 'POST':
        form = ParentMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
            if admin_user:
                msg.recipient = admin_user
                msg.save()
                messages.success(request, "Your message has been sent.")
                return redirect('conversation', user_id=admin_user.id)
            else:
                messages.error(request, "No admin found.")
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = ParentMessageForm()
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')[:10]
    return render(request, 'messagingApp/parent_message_form.html', {'form': form, 'sent_messages': sent_messages})

@login_required
def admin_message_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('home')
    messages_qs = Message.objects.filter(recipient=request.user).select_related('sender')
    conversations = {}
    for msg in messages_qs.order_by('-created_at'):
        sender = msg.sender
        if sender.id not in conversations:
            conversations[sender.id] = {'user': sender, 'last_message': msg, 'unread_count': 0}
        if not msg.is_read:
            conversations[sender.id]['unread_count'] += 1
    return render(request, 'messagingApp/admin_messages.html', {
        'conversations': conversations.values(),
        'unread_count': sum(c['unread_count'] for c in conversations.values()),
    })

@login_required
def admin_message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    return redirect('conversation', user_id=msg.sender.id)

# ---- API endpoints ----

@login_required
def get_recent_messages(request):
    messages_qs = Message.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    data = []
    for m in messages_qs:
        typing_status = UserTypingStatus.objects.filter(user=m.sender).first()
        is_typing = typing_status.is_typing if typing_status else False
        data.append({
            'id': m.id,
            'subject': m.subject,
            'body': m.body[:60],
            'type': m.get_message_type_display(),
            'sender_id': m.sender.id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'created_at': m.created_at.strftime('%d %b %Y, %H:%M'),
            'is_typing': is_typing,
        })
    return JsonResponse({'messages': data})

@login_required
def get_conversation_api(request, user_id):
    other = get_object_or_404(User, id=user_id)
    user = request.user
    messages_qs = Message.objects.filter(
        (Q(sender=user, recipient=other) | Q(sender=other, recipient=user))
    ).order_by('created_at')
    typing_status = UserTypingStatus.objects.filter(user=other).first()
    is_other_typing = typing_status.is_typing if typing_status else False
    data = []
    for m in messages_qs:
        data.append({
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': m.sender.get_full_name() or m.sender.username,
            'body': m.body,
            'created_at': m.created_at.strftime('%H:%M, %d %b %Y'),
            'is_self': m.sender == user,
        })
    return JsonResponse({'messages': data, 'other_typing': is_other_typing})

@login_required
def send_message_api(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    body = data.get('body')
    if not body:
        return JsonResponse({'error': 'Empty message'}, status=400)
    other = get_object_or_404(User, id=user_id)
    msg = Message.objects.create(
        sender=request.user,
        recipient=other,
        subject=f"Re: Conversation with {other.get_full_name() or other.username}",
        message_type='other',
        body=body,
    )
    return JsonResponse({'status': 'ok', 'message': {
        'id': msg.id,
        'sender_id': msg.sender.id,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'body': msg.body,
        'created_at': msg.created_at.strftime('%H:%M, %d %b %Y'),
        'is_self': True,
    }})

@login_required
def typing_indicator(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        is_typing = data.get('is_typing', False)
        status, created = UserTypingStatus.objects.get_or_create(user=request.user)
        status.is_typing = is_typing
        status.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'POST required'}, status=400)

@login_required
def delete_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        message_id = data.get('message_id')
        if not message_id:
            return JsonResponse({'error': 'Message ID required'}, status=400)
        msg = get_object_or_404(Message, id=message_id)
        # Allow sender or staff to delete
        if msg.sender != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        msg.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'POST required'}, status=400)