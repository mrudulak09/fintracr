from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import TaxCalculationService, TaxPlanningService
from .models import TaxProfile, TaxableIncome, TaxDeduction, TaxCalculation
from .forms import TaxProfileForm, TaxableIncomeForm, TaxDeductionForm

@login_required
def tax_dashboard(request):
    context = {
        'profile': TaxProfile.objects.get_or_create(user=request.user)[0],
        'recent_calculations': TaxCalculation.objects.filter(user=request.user).order_by('-year')[:3],
        'deduction_suggestions': TaxPlanningService.suggest_deductions(request.user)
    }
    return render(request, 'tax_management/dashboard.html', context)

@login_required
def update_tax_profile(request):
    profile = TaxProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = TaxProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Tax profile updated successfully')
            return redirect('tax_management:dashboard')
    else:
        form = TaxProfileForm(instance=profile)
    return render(request, 'tax_management/profile_form.html', {'form': form})

@login_required
def calculate_taxes(request, year):
    calculation = TaxCalculationService.calculate_tax_liability(request.user, year)
    return render(request, 'tax_management/tax_calculation.html', {'calculation': calculation}) 