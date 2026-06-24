from django.db import models
from studentsApp.models import Student
from classesApp.models import ClassRoom, Subjects

class Exam(models.Model):
    TERM_CHOICES = (
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
        ('final', 'Final Exam'),
    )
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=TERM_CHOICES, default='term1')
    exam_date = models.DateField()
    max_marks = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject.subject} - {self.class_room.name} ({self.get_term_display()})"

class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Pupil")
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('exam', 'student')

    def percentage(self):
        if self.exam.max_marks:
            return (float(self.marks_obtained) / self.exam.max_marks) * 100
        return 0

    def grade(self):
        p = self.percentage()
        if p >= 80: return 'A'
        if p >= 70: return 'B'
        if p >= 60: return 'C'
        if p >= 50: return 'D'
        if p >= 40: return 'E'
        return 'F'

    def __str__(self):
        # Show full name if available, otherwise username
        name = self.student.user.get_full_name() or self.student.user.username
        return f"{name} - {self.exam.subject.subject}: {self.marks_obtained}"