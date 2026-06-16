from django.contrib import admin
from .models import Parent

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'user__email')