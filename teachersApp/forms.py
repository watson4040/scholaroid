from django import forms
from .models import Teacher, PupilReport, AcademicRecord, Assignment, BehaviorLog, Timetable
from classesApp.models import ClassRoom, Subjects


class TeacherAdminForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'assigned_class']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'assigned_class': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


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


# ---------- NEW FORMS ----------

class AcademicRecordForm(forms.ModelForm):
    class Meta:
        model = AcademicRecord
        fields = ['pupil', 'subject', 'class_room', 'term', 'academic_year', 'exam_type', 'marks', 'max_marks', 'remark']
        widgets = {
            'pupil': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025/2026'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any remark...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        marks = cleaned_data.get('marks')
        max_marks = cleaned_data.get('max_marks')
        if marks is not None and max_marks is not None and marks > max_marks:
            raise forms.ValidationError("Marks cannot exceed maximum marks.")
        return cleaned_data


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'class_room', 'due_date', 'file_upload']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the assignment'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'class_room': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'file_upload': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BehaviorLogForm(forms.ModelForm):
    class Meta:
        model = BehaviorLog
        fields = ['pupil', 'category', 'note', 'conduct_remark', 'is_report_card_remark']
        widgets = {
            'pupil': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed behavior note...'}),
            'conduct_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'For report card...'}),
            'is_report_card_remark': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }