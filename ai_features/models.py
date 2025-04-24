from django.db import models
from django.conf import settings

class FinancialAdvice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    advice_type = models.CharField(max_length=50, choices=[
        ('SAVING', 'Saving Tips'),
        ('BUDGET', 'Budget Adjustments'),
        ('INVESTMENT', 'Investment Options')
    ])
    advice_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class ExpenseAnomaly(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    anomaly_type = models.CharField(max_length=50, choices=[
        ('UNUSUAL_AMOUNT', 'Unusual Amount'),
        ('UNUSUAL_CATEGORY', 'Unusual Category'),
        ('UNUSUAL_FREQUENCY', 'Unusual Frequency')
    ])
    description = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)

class FinancialForecast(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    forecast_type = models.CharField(max_length=50, choices=[
        ('INCOME', 'Income Forecast'),
        ('EXPENSE', 'Expense Forecast'),
        ('CASHFLOW', 'Cash Flow Forecast')
    ])
    forecast_date = models.DateField()
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class FinancialCalculation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    result = models.TextField()
    explanation = models.TextField()
    insights = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Calculation: {self.query[:30]}... = {self.result[:30]}..."
    
    class Meta:
        ordering = ['-created_at'] 