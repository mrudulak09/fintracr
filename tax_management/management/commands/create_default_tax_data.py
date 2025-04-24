from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tax_management.models import TaxProfile, TaxableIncome, TaxDeduction, TaxCalculation
from decimal import Decimal
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates default tax management data'

    def handle(self, *args, **kwargs):
        # Default tax profiles
        default_profiles = [
            {
                'tax_id': 'TAX123456',
                'filing_status': 'SINGLE'
            }
        ]

        # Default taxable income
        default_incomes = [
            {
                'year': 2024,
                'income_type': 'SALARY',
                'amount': Decimal('60000.00')
            },
            {
                'year': 2024,
                'income_type': 'INVESTMENT',
                'amount': Decimal('5000.00')
            }
        ]

        # Default deductions
        default_deductions = [
            {
                'year': 2024,
                'deduction_type': 'STANDARD',
                'amount': Decimal('12950.00'),
                'description': 'Standard deduction for single filer'
            },
            {
                'year': 2024,
                'deduction_type': 'ITEMIZED',
                'amount': Decimal('2000.00'),
                'description': 'Charitable contributions'
            }
        ]

        users = User.objects.all()
        if not users.exists():
            self.stdout.write('No users found. Please create a user first.')
            return

        for user in users:
            # Create tax profile
            for profile in default_profiles:
                TaxProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'tax_id': profile['tax_id'],
                        'filing_status': profile['filing_status']
                    }
                )

            # Create taxable income
            for income in default_incomes:
                TaxableIncome.objects.get_or_create(
                    user=user,
                    year=income['year'],
                    income_type=income['income_type'],
                    amount=income['amount']
                )

            # Create deductions
            for deduction in default_deductions:
                TaxDeduction.objects.get_or_create(
                    user=user,
                    year=deduction['year'],
                    deduction_type=deduction['deduction_type'],
                    amount=deduction['amount'],
                    description=deduction['description']
                )

            # Create tax calculation
            total_income = sum(income['amount'] for income in default_incomes)
            total_deductions = sum(deduction['amount'] for deduction in default_deductions)
            taxable_income = total_income - total_deductions
            tax_liability = taxable_income * Decimal('0.22')  # Simple 22% tax rate

            TaxCalculation.objects.get_or_create(
                user=user,
                year=2024,
                total_income=total_income,
                total_deductions=total_deductions,
                taxable_income=taxable_income,
                tax_liability=tax_liability
            )

        self.stdout.write(self.style.SUCCESS('Successfully created default tax data')) 