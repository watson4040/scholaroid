from django import forms
from .models import EnrollmentRequest

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = EnrollmentRequest
        # Remove 'pupil_class' from fields
        fields = ['parent_name', 'parent_email', 'parent_phone', 'pupil_name', 'pupil_dob', 'message']
        widgets = {
            'pupil_dob': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }