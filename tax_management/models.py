from django.db import models
from django.conf import settings

class TaxProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tax_id = models.CharField(max_length=50, blank=True)
    filing_status = models.CharField(max_length=50, choices=[
        ('SINGLE', 'Single'),
        ('MARRIED_JOINT', 'Married Filing Jointly'),
        ('MARRIED_SEPARATE', 'Married Filing Separately'),
        ('HEAD_HOUSEHOLD', 'Head of Household')
    ])
    
class TaxableIncome(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.IntegerField()
    income_type = models.CharField(max_length=50, choices=[
        ('SALARY', 'Salary'),
        ('BUSINESS', 'Business Income'),
        ('INVESTMENT', 'Investment Income'),
        ('OTHER', 'Other Income')
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
class TaxDeduction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.IntegerField()
    deduction_type = models.CharField(max_length=50, choices=[
        ('STANDARD', 'Standard Deduction'),
        ('ITEMIZED', 'Itemized Deduction'),
        ('BUSINESS', 'Business Expense'),
        ('OTHER', 'Other Deduction')
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

class TaxCalculation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.IntegerField()
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_income = models.DecimalField(max_digits=10, decimal_places=2)
    tax_liability = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True) 