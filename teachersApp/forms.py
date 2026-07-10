from django import forms
from .models import Teacher, PupilReport
from classesApp.models import ClassRoom, Subjects

# ---- Admin Teacher Form ----
class TeacherAdminForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'assigned_class', 'hire_date']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'assigned_class': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# ---- Pupil Report Form (for teacher comments) ----
class PupilReportForm(forms.ModelForm):
    class Meta:
        model = PupilReport
        fields = ['term', 'academic_year', 'comment', 'is_submitted']
        widgets = {
            'term': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025/2026'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your comments about the pupil...'}),
            'is_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }