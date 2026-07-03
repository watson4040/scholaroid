from django import forms
from .models import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['class_room', 'subject', 'term', 'exam_date', 'max_marks', 'description']
        widgets = {
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}, choices=Exam.TERM_CHOICES),
            'exam_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes'}),
        }