from django.contrib import admin

from .models import (
    FeeStructure,
    Invoice,
    Payment,
    Discount,
    Expense,
    Scholarship,
    SchoolPromotion,
    SubscriptionPlan,
    SchoolSubscription,
    FinanceDashboard,
    FinancialReport,
    StudentService,
    LicenseKey,
    PaymentAuditLog,
)


# ==========================================================
# FEE STRUCTURE
# ==========================================================

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "amount",
        "due_date",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "due_date",
    )


# ==========================================================
# INVOICE
# ==========================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "fee_structure",
        "amount_due",
        "amount_paid",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "fee_structure",
    )

    search_fields = (
        "student__user__username",
    )

    readonly_fields = (
        "amount_paid",
    )


# ==========================================================
# PAYMENT
# ==========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "amount",
        "payment_date",
        "receipt_number",
        "recorded_by",
    )

    list_filter = (
        "payment_date",
    )

    search_fields = (
        "receipt_number",
        "invoice__student__user__username",
    )

    readonly_fields = (
        "receipt_number",
    )


# ==========================================================
# DISCOUNT
# ==========================================================

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# EXPENSE
# ==========================================================

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# SCHOLARSHIP
# ==========================================================

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# SCHOOL PROMOTION
# ==========================================================

@admin.register(SchoolPromotion)
class SchoolPromotionAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# SUBSCRIPTION PLAN
# ==========================================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# SCHOOL SUBSCRIPTION
# ==========================================================

@admin.register(SchoolSubscription)
class SchoolSubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# FINANCE DASHBOARD
# ==========================================================

@admin.register(FinanceDashboard)
class FinanceDashboardAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# FINANCIAL REPORT
# ==========================================================

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# STUDENT SERVICE
# ==========================================================

@admin.register(StudentService)
class StudentServiceAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# LICENSE KEY
# ==========================================================

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )


# ==========================================================
# PAYMENT AUDIT LOG
# ==========================================================

@admin.register(PaymentAuditLog)
class PaymentAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "__str__",
    )