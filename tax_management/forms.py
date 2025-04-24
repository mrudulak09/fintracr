from django import forms
from .models import TaxProfile, TaxableIncome, TaxDeduction

class TaxProfileForm(forms.ModelForm):
    class Meta:
        model = TaxProfile
        fields = ['tax_id', 'filing_status']
        widgets = {
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'filing_status': forms.Select(attrs={'class': 'form-control'}),
        }

class TaxableIncomeForm(forms.ModelForm):
    class Meta:
        model = TaxableIncome
        fields = ['year', 'income_type', 'amount']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'income_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TaxDeductionForm(forms.ModelForm):
    class Meta:
        model = TaxDeduction
        fields = ['year', 'deduction_type', 'amount', 'description']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'deduction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 