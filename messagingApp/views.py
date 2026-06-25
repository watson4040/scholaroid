from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Message
from .forms import ParentMessageForm
from accountsApp.models import User

@login_required
def user_inbox(request):
    """Show all conversations grouped by the other participant."""
    user = request.user
    messages_qs = Message.objects.filter(Q(sender=user) | Q(recipient=user)).select_related('sender', 'recipient')
    conversations = {}
    for msg in messages_qs.order_by('-created_at'):
        other = msg.recipient if msg.sender == user else msg.sender
        if other:
            if other.id not in conversations:
                conversations[other.id] = {
                    'user': other,
                    'last_message': msg,
                    'unread_count': 0,
                }
            if msg.recipient == user and not msg.is_read:
                conversations[other.id]['unread_count'] += 1
    context = {
        'conversations': conversations.values(),
    }
    return render(request, 'messagingApp/inbox.html', context)

@login_required
def conversation(request, user_id):
    """View full conversation between current user and another user."""
    other = get_object_or_404(User, id=user_id)
    user = request.user

    # Prevent chatting with yourself
    if user == other:
        messages.error(request, "You cannot message yourself.")
        return redirect('inbox')

    # Mark all messages from other to user as read
    Message.objects.filter(sender=other, recipient=user, is_read=False).update(is_read=True)

    # Get all messages between the two users
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

    context = {
        'other': other,
        'messages': messages_qs,
    }
    return render(request, 'messagingApp/conversation.html', context)

@login_required
def parent_send_message(request):
    """Allow parent to send a new message to admin (creates a new conversation)."""
    if request.method == 'POST':
        form = ParentMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            # Find an admin (superuser or staff)
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                msg.recipient = admin_user
                msg.save()
                messages.success(request, "Your message has been sent.")
                # Redirect to the conversation with that admin
                return redirect('conversation', user_id=admin_user.id)
            else:
                messages.error(request, "No admin found. Please contact support.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ParentMessageForm()

    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')[:10]
    return render(request, 'messagingApp/parent_message_form.html', {
        'form': form,
        'sent_messages': sent_messages,
    })

@login_required
def admin_message_list(request):
    """Admin sees all conversations with parents (grouped by sender)."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('home')

    messages_qs = Message.objects.filter(recipient=request.user).select_related('sender')
    conversations = {}
    for msg in messages_qs.order_by('-created_at'):
        sender = msg.sender
        if sender.id not in conversations:
            conversations[sender.id] = {
                'user': sender,
                'last_message': msg,
                'unread_count': 0,
            }
        if not msg.is_read:
            conversations[sender.id]['unread_count'] += 1

    context = {
        'conversations': conversations.values(),
        'unread_count': sum(c['unread_count'] for c in conversations.values()),
    }
    return render(request, 'messagingApp/admin_messages.html', context)

@login_required
def admin_message_detail(request, pk):
    """Redirect admin to the conversation with the sender of the message."""
    msg = get_object_or_404(Message, pk=pk)
    return redirect('conversation', user_id=msg.sender.id)