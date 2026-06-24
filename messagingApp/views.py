from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import ParentMessageForm
from accountsApp.models import User

@login_required
def parent_send_message(request):
    """Parent sends a message to the admin (first superuser)."""
    if request.method == 'POST':
        form = ParentMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            # Find any admin (superuser or staff) as recipient
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                msg.recipient = admin_user
                msg.save()
                messages.success(request, "Your message has been sent to the school administration.")
            else:
                messages.error(request, "No admin recipient found. Please contact technical support.")
            return redirect('parent_send_message')
    else:
        form = ParentMessageForm()
    return render(request, 'messagingApp/parent_message_form.html', {'form': form})

@login_required
def admin_message_list(request):
    """Admin view: list all messages received by this admin."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('home')
    messages_list = Message.objects.filter(recipient=request.user).select_related('sender')
    unread_count = messages_list.filter(is_read=False).count()
    return render(request, 'messagingApp/admin_messages.html', {
        'messages': messages_list,
        'unread_count': unread_count,
    })


@login_required
def admin_message_detail(request, pk):
    """Admin view a single message, mark as read, and reply."""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('home')
    
    msg = get_object_or_404(Message, pk=pk)
    
    # Mark as read if the admin is the recipient
    if msg.recipient == request.user and not msg.is_read:
        msg.is_read = True
        msg.save()
    
    if request.method == 'POST':
        reply_body = request.POST.get('reply_body')
        if reply_body:
            # Create the reply
            reply = Message.objects.create(
                sender=request.user,
                recipient=msg.sender,  # Send back to the original sender
                subject=f"RE: {msg.subject}",
                message_type=msg.message_type,
                body=reply_body,
                parent_message_id=msg  # Link to the original message
            )
            messages.success(request, "Reply sent successfully.")
            return redirect('admin_message_detail', pk=pk)
        else:
            messages.error(request, "Reply cannot be empty.")
    
    return render(request, 'messagingApp/admin_message_detail.html', {'message': msg})