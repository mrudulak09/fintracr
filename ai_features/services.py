import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.db.models import Sum, Avg
from .models import FinancialAdvice, ExpenseAnomaly, FinancialForecast
from django.contrib.auth import get_user_model
from .gemini_service import GeminiService
from budget_section.models import Transaction, Category
from my_finances.models import Income, Outcome, Balance
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FinancialAdviceService:
    @staticmethod
    def generate_saving_tips(user):
        try:
            # Get user's financial data
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Get income data
            total_income = Income.objects.filter(
                user=user,
                date__month=current_month,
                date__year=current_year
            ).aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
            
            # Get expense data
            total_expenses = Outcome.objects.filter(
                user=user,
                date__month=current_month,
                date__year=current_year
            ).aggregate(Sum('value'))['value__sum'] or Decimal('0.00')
            
            # Get savings data (simplified)
            latest_balance = Balance.objects.filter(user=user).order_by('-date').first()
            total_savings = latest_balance.value if latest_balance else Decimal('0.00')
            
            # Get debt data from transactions (simplified - assuming negative transactions are debts)
            try:
                total_debt = Transaction.objects.filter(
                    user=user,
                    amount__lt=0
                ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
                total_debt = abs(total_debt)
            except Exception as e:
                logger.warning(f"Error getting transaction data: {str(e)}")
                total_debt = Decimal('0.00')
            
            # Prepare data for Gemini API
            user_data = {
                'income': float(total_income),
                'expenses': float(total_expenses),
                'savings': float(total_savings),
                'debt': float(total_debt)
            }
            
            # Generate advice using Gemini
            advice_text = GeminiService.generate_financial_advice(user_data)
            
            # Create and return the advice object
            return FinancialAdvice.objects.create(
                user=user,
                advice_type='SAVING',
                advice_text=advice_text
            )
        except Exception as e:
            logger.error(f"Error generating financial advice: {str(e)}")
            return FinancialAdvice.objects.create(
                user=user,
                advice_type='SAVING',
                advice_text="Unable to generate personalized advice due to insufficient data. Please add more financial information to receive better recommendations."
            )

class AnomalyDetectionService:
    @staticmethod
    def detect_anomalies(user):
        try:
            # Get recent transactions
            try:
                recent_transactions = Transaction.objects.filter(
                    user=user,
                    date__gte=datetime.now() - timedelta(days=90)
                ).order_by('-date')[:50]  # Last 50 transactions or within 90 days
            except Exception as tx_error:
                logger.warning(f"Error getting transactions: {str(tx_error)}")
                recent_transactions = []
            
            if not recent_transactions:
                # Create sample anomaly if no transactions found
                anomaly = ExpenseAnomaly.objects.create(
                    user=user,
                    amount=Decimal('0.00'),
                    category='General',
                    anomaly_type='UNUSUAL_AMOUNT',
                    description="Not enough transaction data to analyze. Please add more transactions."
                )
                return [anomaly]
            
            # Prepare transaction data for Gemini API
            transaction_data = []
            for transaction in recent_transactions:
                try:
                    category_name = transaction.category.name if hasattr(transaction, 'category') and transaction.category else 'Uncategorized'
                    transaction_data.append({
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'category': category_name,
                        'amount': float(transaction.amount)
                    })
                except AttributeError as attr_error:
                    logger.warning(f"Error processing transaction {transaction.id}: {str(attr_error)}")
            
            if not transaction_data:
                anomaly = ExpenseAnomaly.objects.create(
                    user=user,
                    amount=Decimal('0.00'),
                    category='General',
                    anomaly_type='UNUSUAL_AMOUNT',
                    description="Error processing transaction data. Please check your transaction records."
                )
                return [anomaly]
            
            # Detect anomalies using Gemini
            gemini_anomalies = GeminiService.detect_anomalies(transaction_data)
            
            # Create anomaly objects
            anomalies = []
            for anomaly_data in gemini_anomalies:
                anomaly_type = 'UNUSUAL_AMOUNT'  # Default
                if 'type' in anomaly_data:
                    if 'category' in anomaly_data['type'].lower():
                        anomaly_type = 'UNUSUAL_CATEGORY'
                    elif 'frequency' in anomaly_data['type'].lower():
                        anomaly_type = 'UNUSUAL_FREQUENCY'
                
                # Extract amount from transaction if available
                amount = Decimal('0.00')
                category = 'Unknown'
                if 'transaction' in anomaly_data and anomaly_data['transaction'] != 'N/A':
                    # Try to extract amount from transaction description
                    try:
                        amount_str = anomaly_data['transaction'].split('$')[-1].split(',')[0].strip()
                        amount = Decimal(amount_str)
                    except (IndexError, ValueError, InvalidOperation):
                        try:
                            # Try to extract with rupee symbol
                            if '₹' in anomaly_data['transaction']:
                                amount_str = anomaly_data['transaction'].split('₹')[-1].split(',')[0].strip()
                                amount = Decimal(amount_str)
                            # Try to extract with "Rs." format
                            elif 'Rs.' in anomaly_data['transaction']:
                                amount_str = anomaly_data['transaction'].split('Rs.')[-1].split(',')[0].strip()
                                amount = Decimal(amount_str)
                            # Try to extract with "INR" format
                            elif 'INR' in anomaly_data['transaction']:
                                amount_str = anomaly_data['transaction'].split('INR')[-1].split(',')[0].strip()
                                amount = Decimal(amount_str)
                            else:
                                amount = Decimal('0.00')
                        except (IndexError, ValueError, InvalidOperation):
                            amount = Decimal('0.00')
                    
                    # Try to extract category from transaction description
                    try:
                        if 'Category:' in anomaly_data['transaction']:
                            category = anomaly_data['transaction'].split('Category:')[-1].split(',')[0].strip()
                    except IndexError:
                        pass
                
                anomaly = ExpenseAnomaly.objects.create(
                    user=user,
                    amount=amount,
                    category=category,
                    anomaly_type=anomaly_type,
                    description=anomaly_data.get('description', 'Anomaly detected')
                )
                anomalies.append(anomaly)
            
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            anomaly = ExpenseAnomaly.objects.create(
                user=user,
                amount=Decimal('0.00'),
                category='General',
                anomaly_type='UNUSUAL_AMOUNT',
                description="An error occurred while detecting anomalies. Please try again later."
            )
            return [anomaly]

class ForecastingService:
    @staticmethod
    def forecast_expenses(user):
        try:
            # Get historical expense data (last 12 months)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            # Aggregate expenses by month
            try:
                expenses_by_month = Outcome.objects.filter(
                    user=user,
                    date__gte=start_date,
                    date__lte=end_date
                ).values('date__year', 'date__month').annotate(
                    total_amount=Sum('value')
                ).order_by('date__year', 'date__month')
            except Exception as exp_error:
                logger.warning(f"Error getting expense data: {str(exp_error)}")
                expenses_by_month = []
            
            # Prepare data for Gemini API
            historical_data = []
            for expense in expenses_by_month:
                try:
                    month_date = datetime(expense['date__year'], expense['date__month'], 1).date()
                    historical_data.append({
                        'date': month_date.strftime('%Y-%m-%d'),
                        'amount': float(expense['total_amount'])
                    })
                except (KeyError, ValueError) as data_error:
                    logger.warning(f"Error processing expense data: {str(data_error)}")
            
            # If insufficient data, create sample forecasts
            if len(historical_data) < 3:
                # Create sample forecasts
                forecasts = []
                for forecast_type, amount, confidence in [
                    ('EXPENSE', 3000, 0.6),
                    ('INCOME', 5000, 0.7),
                    ('CASHFLOW', 2000, 0.5)
                ]:
                    forecast = FinancialForecast.objects.create(
                        user=user,
                        forecast_type=forecast_type,
                        forecast_date=datetime.now().date() + timedelta(days=30),
                        predicted_amount=Decimal(str(amount)),
                        confidence_score=confidence
                    )
                    forecasts.append(forecast)
                
                return forecasts
            
            # Generate forecasts using Gemini
            forecasts = []
            
            # Expense forecast
            expense_forecast_data = GeminiService.generate_forecast(historical_data, 'EXPENSE')
            
            # Create Expense forecast objects
            if 'predictions' in expense_forecast_data:
                for i, prediction in enumerate(expense_forecast_data['predictions']):
                    forecast_date = datetime.now().date() + timedelta(days=30 * (i + 1))
                    amount = prediction.get('amount', 0)
                    confidence = prediction.get('confidence', 0.5)
                    
                    forecast = FinancialForecast.objects.create(
                        user=user,
                        forecast_type='EXPENSE',
                        forecast_date=forecast_date,
                        predicted_amount=Decimal(str(amount)),
                        confidence_score=confidence
                    )
                    forecasts.append(forecast)
            
            # Get income data
            try:
                income_by_month = Income.objects.filter(
                    user=user,
                    date__gte=start_date,
                    date__lte=end_date
                ).values('date__year', 'date__month').annotate(
                    total_amount=Sum('value')
                ).order_by('date__year', 'date__month')
            except Exception as inc_error:
                logger.warning(f"Error getting income data: {str(inc_error)}")
                income_by_month = []
            
            income_data = []
            for income in income_by_month:
                try:
                    month_date = datetime(income['date__year'], income['date__month'], 1).date()
                    income_data.append({
                        'date': month_date.strftime('%Y-%m-%d'),
                        'amount': float(income['total_amount'])
                    })
                except (KeyError, ValueError) as data_error:
                    logger.warning(f"Error processing income data: {str(data_error)}")
            
            # Income forecast
            if len(income_data) >= 3:
                income_forecast_data = GeminiService.generate_forecast(income_data, 'INCOME')
                
                # Create Income forecast objects
                if 'predictions' in income_forecast_data:
                    for i, prediction in enumerate(income_forecast_data['predictions']):
                        forecast_date = datetime.now().date() + timedelta(days=30 * (i + 1))
                        amount = prediction.get('amount', 0)
                        confidence = prediction.get('confidence', 0.5)
                        
                        forecast = FinancialForecast.objects.create(
                            user=user,
                            forecast_type='INCOME',
                            forecast_date=forecast_date,
                            predicted_amount=Decimal(str(amount)),
                            confidence_score=confidence
                        )
                        forecasts.append(forecast)
            
            # Cash flow forecast (combine both)
            if len(income_data) >= 3 and len(historical_data) >= 3:
                # Calculate historical cash flow
                cashflow_data = []
                income_dict = {d['date']: d['amount'] for d in income_data}
                expense_dict = {d['date']: d['amount'] for d in historical_data}
                
                # Get all unique dates
                all_dates = sorted(set(list(income_dict.keys()) + list(expense_dict.keys())))
                
                for date in all_dates:
                    income_amount = income_dict.get(date, 0)
                    expense_amount = expense_dict.get(date, 0)
                    cashflow_amount = income_amount - expense_amount
                    
                    cashflow_data.append({
                        'date': date,
                        'amount': cashflow_amount
                    })
                    
                cashflow_forecast_data = GeminiService.generate_forecast(cashflow_data, 'CASHFLOW')
                
                # Create Cashflow forecast objects
                if 'predictions' in cashflow_forecast_data:
                    for i, prediction in enumerate(cashflow_forecast_data['predictions']):
                        forecast_date = datetime.now().date() + timedelta(days=30 * (i + 1))
                        amount = prediction.get('amount', 0)
                        confidence = prediction.get('confidence', 0.5)
                        
                        forecast = FinancialForecast.objects.create(
                            user=user,
                            forecast_type='CASHFLOW',
                            forecast_date=forecast_date,
                            predicted_amount=Decimal(str(amount)),
                            confidence_score=confidence
                        )
                        forecasts.append(forecast)
            
            return forecasts
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            # Return sample forecasts in case of error
            forecasts = []
            for forecast_type, amount, confidence in [
                ('EXPENSE', 3000, 0.5),
                ('INCOME', 5000, 0.5),
                ('CASHFLOW', 2000, 0.5)
            ]:
                forecast = FinancialForecast.objects.create(
                    user=user,
                    forecast_type=forecast_type,
                    forecast_date=datetime.now().date() + timedelta(days=30),
                    predicted_amount=Decimal(str(amount)),
                    confidence_score=confidence
                )
                forecasts.append(forecast)
            
            return forecasts 