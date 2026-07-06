from django import forms
from .models import Exam
from classesApp.models import ClassRoom, Subjects

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

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # Limit choices to teacher's assigned classes/subjects
            self.fields['class_room'].queryset = teacher.assigned_class.all()
            self.fields['subject'].queryset = teacher.subject.all()
        else:
            # For admin: show all
            self.fields['class_room'].queryset = ClassRoom.objects.all()
            self.fields['subject'].queryset = Subjects.objects.all()