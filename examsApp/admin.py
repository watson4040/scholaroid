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
    # Add save_on_top so buttons appear both at top and bottom
    save_on_top = True
    # Optionally set list_per_page to control pagination
    list_per_page = 25

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam__class_room', 'exam__term')
    search_fields = ('student__user__username', 'student__user__email')
    readonly_fields = ('grade',)
    save_on_top = True