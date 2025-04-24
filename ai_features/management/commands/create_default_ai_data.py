from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai_features.models import FinancialAdvice, ExpenseAnomaly, FinancialForecast
from datetime import datetime, timedelta
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates default AI feature data'

    def handle(self, *args, **kwargs):
        # Default financial advice
        default_advice = [
            {
                'advice_type': 'SAVING',
                'advice_text': 'Consider setting aside 20% of your monthly income for savings and emergencies.'
            },
            {
                'advice_type': 'BUDGET',
                'advice_text': 'Try using the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings.'
            },
            {
                'advice_type': 'INVESTMENT',
                'advice_text': 'Consider diversifying your investment portfolio across stocks, bonds, and real estate.'
            },
        ]

        # Default anomalies
        default_anomalies = [
            {
                'amount': Decimal('1500.00'),
                'category': 'Entertainment',
                'anomaly_type': 'UNUSUAL_AMOUNT',
                'description': 'Unusually high entertainment spending detected'
            },
            {
                'amount': Decimal('2000.00'),
                'category': 'Shopping',
                'anomaly_type': 'UNUSUAL_FREQUENCY',
                'description': 'Multiple large shopping transactions in short period'
            },
        ]

        # Default forecasts
        default_forecasts = [
            {
                'forecast_type': 'INCOME',
                'predicted_amount': Decimal('5000.00'),
                'confidence_score': 0.85,
                'forecast_date': datetime.now().date() + timedelta(days=30)
            },
            {
                'forecast_type': 'EXPENSE',
                'predicted_amount': Decimal('3500.00'),
                'confidence_score': 0.75,
                'forecast_date': datetime.now().date() + timedelta(days=30)
            },
            {
                'forecast_type': 'CASHFLOW',
                'predicted_amount': Decimal('1500.00'),
                'confidence_score': 0.70,
                'forecast_date': datetime.now().date() + timedelta(days=30)
            },
        ]

        # Get or create a default user if needed
        users = User.objects.all()
        if not users.exists():
            self.stdout.write('No users found. Please create a user first.')
            return

        for user in users:
            # Create advice
            for advice in default_advice:
                FinancialAdvice.objects.get_or_create(
                    user=user,
                    advice_type=advice['advice_type'],
                    advice_text=advice['advice_text']
                )

            # Create anomalies
            for anomaly in default_anomalies:
                ExpenseAnomaly.objects.get_or_create(
                    user=user,
                    amount=anomaly['amount'],
                    category=anomaly['category'],
                    anomaly_type=anomaly['anomaly_type'],
                    description=anomaly['description']
                )

            # Create forecasts
            for forecast in default_forecasts:
                FinancialForecast.objects.get_or_create(
                    user=user,
                    forecast_type=forecast['forecast_type'],
                    predicted_amount=forecast['predicted_amount'],
                    confidence_score=forecast['confidence_score'],
                    forecast_date=forecast['forecast_date']
                )

        self.stdout.write(self.style.SUCCESS('Successfully created default AI data')) 