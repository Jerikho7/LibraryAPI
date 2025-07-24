from django.contrib import admin

from loans.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "book",
        "loan_date",
        "return_date",
    )
