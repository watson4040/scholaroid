from django.contrib import admin
from .models import Exam, ExamResult

class ExamResultInline(admin.TabularInline):
    model = ExamResult
    extra = 3
    fields = ('student', 'marks_obtained', 'remarks')
    autocomplete_fields = ['student']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_room', 'term', 'exam_date', 'max_marks')
    list_filter = ('term', 'class_room', 'subject')
    search_fields = ('subject__subject', 'class_room__name')
    inlines = [ExamResultInline]

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam__class_room', 'exam__term')
    search_fields = ('student__user__username', 'student__user__email')
    readonly_fields = ('grade',)