from django import forms
from .models import Message

class ParentMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_type', 'subject', 'body']
        widgets = {
            'message_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Fee structure for Grade 5'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message here...'}),
        }
        labels = {
            'message_type': 'What is this about?',
            'subject': 'Subject',
            'body': 'Message',
        }