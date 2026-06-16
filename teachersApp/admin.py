from django.contrib import admin
from .models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_subjects', 'get_classes_assigned')
    search_fields = ('user__username', 'user__email')

    def get_subjects(self, obj):
        # If subject is a ManyToManyField, show comma-separated list
        if hasattr(obj, 'subject'):
            subjects = obj.subject.all()
            return ', '.join(str(subj) for subj in subjects[:3])  # limit to 3
        return '-'
    get_subjects.short_description = 'Subjects'

    def get_classes_assigned(self, obj):
        # If class_assigned is a ManyToManyField
        if hasattr(obj, 'class_assigned'):
            classes = obj.class_assigned.all()
            return ', '.join(str(cls) for cls in classes[:3])
        return '-'
    get_classes_assigned.short_description = 'Classes Assigned'

admin.site.register(Teacher, TeacherAdmin)