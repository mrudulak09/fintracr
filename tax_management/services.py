from decimal import Decimal
from django.db.models import Sum
from .models import TaxProfile, TaxableIncome, TaxDeduction, TaxCalculation
from django.contrib.auth import get_user_model

User = get_user_model()

class TaxCalculationService:
    @staticmethod
    def calculate_tax_liability(user, year):
        # Sample calculation for demonstration
        total_income = Decimal('60000.00')  # Sample income
        total_deductions = Decimal('12000.00')  # Sample deductions
        taxable_income = total_income - total_deductions

        # Simple tax calculation (22% flat rate for demonstration)
        tax_liability = taxable_income * Decimal('0.22')

        return TaxCalculation.objects.create(
            user=user,
            year=year,
            total_income=total_income,
            total_deductions=total_deductions,
            taxable_income=taxable_income,
            tax_liability=tax_liability
        )

class TaxPlanningService:
    @staticmethod
    def suggest_deductions(user):
        """Generate sample tax deduction suggestions."""
        suggestions = [
            "Consider contributing to retirement accounts for tax benefits",
            "Track your charitable contributions for tax deductions",
            "Keep records of work-related expenses",
            "Consider mortgage interest deductions if you own a home"
        ]
        return suggestions

    @staticmethod
    def estimate_quarterly_taxes(user, year):
        """Provide a sample quarterly tax estimate."""
        return Decimal('3000.00')  # Sample quarterly payment 