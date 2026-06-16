from django.contrib import admin
from .models import FeeStructure, Invoice, Payment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'due_date')
    search_fields = ('name',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_due', 'amount_paid', 'balance', 'status')
    list_filter = ('status', 'fee_structure')
    search_fields = ('student__user__username',)
    readonly_fields = ('amount_paid',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'receipt_number')
    list_filter = ('payment_date',)
    readonly_fields = ('receipt_number',)