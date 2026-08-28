from django.contrib import admin
from .models import ClassRoom, Subjects

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'capacity')

@admin.register(Subjects)
class SubjectsAdmin(admin.ModelAdmin):
    list_display = ('subject',)