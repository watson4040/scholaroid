from django.db import models
from django.conf import settings

class Message(models.Model):
    MESSAGE_TYPES = (
        ('inquiry', 'General Inquiry'),
        ('fee', 'Fees Schedule'),
        ('performance', 'Child Performance'),
        ('schedule', 'School Schedule'),
        ('other', 'Other'),
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    subject = models.CharField(max_length=200)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='inquiry')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    parent_message_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} from {self.sender.email}"


# New model for typing status
class UserTypingStatus(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} typing: {self.is_typing}"