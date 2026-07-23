from django.contrib import admin
from .models import Teacher, PupilReport, AcademicRecord, Assignment, BehaviorLog, Timetable


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_subjects', 'get_classes_assigned', 'hire_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('hire_date',)
    filter_horizontal = ('subject', 'assigned_class')
    exclude = ('hire_date',)  # Exclude auto_add_now field

    def get_subjects(self, obj):
        subjects = obj.subject.all()
        return ', '.join(str(sub) for sub in subjects[:3]) + (' ...' if subjects.count() > 3 else '')
    get_subjects.short_description = 'Subjects'

    def get_classes_assigned(self, obj):
        classes = obj.assigned_class.all()
        return ', '.join(str(cls) for cls in classes[:3]) + (' ...' if classes.count() > 3 else '')
    get_classes_assigned.short_description = 'Classes Assigned'


class PupilReportAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'term', 'academic_year', 'teacher', 'is_submitted', 'updated_at')
    list_filter = ('term', 'academic_year', 'is_submitted')
    search_fields = ('pupil__user__username', 'teacher__user__username', 'comment')
    raw_id_fields = ('pupil', 'teacher')


class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'subject', 'class_room', 'term', 'exam_type', 'marks', 'max_marks', 'date_recorded')
    list_filter = ('term', 'exam_type', 'subject', 'class_room')
    search_fields = ('pupil__user__username', 'subject__name', 'remark')
    raw_id_fields = ('pupil', 'subject', 'class_room', 'teacher')


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_room', 'teacher', 'due_date', 'created_at')
    list_filter = ('subject', 'class_room', 'due_date')
    search_fields = ('title', 'description')
    raw_id_fields = ('subject', 'class_room', 'teacher')


class BehaviorLogAdmin(admin.ModelAdmin):
    list_display = ('pupil', 'teacher', 'category', 'date', 'is_report_card_remark')
    list_filter = ('category', 'is_report_card_remark', 'date')
    search_fields = ('pupil__user__username', 'note', 'conduct_remark')
    raw_id_fields = ('pupil', 'teacher')


class TimetableAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'class_room', 'subject', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'class_room', 'subject')
    search_fields = ('teacher__user__username', 'subject__name')
    raw_id_fields = ('teacher', 'class_room', 'subject')


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(PupilReport, PupilReportAdmin)
admin.site.register(AcademicRecord, AcademicRecordAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(BehaviorLog, BehaviorLogAdmin)
admin.site.register(Timetable, TimetableAdmin)