from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import FinancialAdviceService, AnomalyDetectionService, ForecastingService
from .models import FinancialAdvice, ExpenseAnomaly, FinancialForecast, FinancialCalculation
from .gemini_service import GeminiService
import json

@login_required
def dashboard(request):
    context = {
        'advice': FinancialAdvice.objects.filter(user=request.user).order_by('-created_at')[:5],
        'anomalies': ExpenseAnomaly.objects.filter(user=request.user).order_by('-detected_at')[:5],
        'forecasts': FinancialForecast.objects.filter(user=request.user).order_by('-created_at')[:3]
    }
    return render(request, 'ai_features/dashboard.html', context)

@login_required
def generate_advice(request):
    advice = FinancialAdviceService.generate_saving_tips(request.user)
    return JsonResponse({'message': 'Advice generated successfully'})

@login_required
def detect_anomalies(request):
    anomalies = AnomalyDetectionService.detect_anomalies(request.user)
    return JsonResponse({'message': f'Detected {len(anomalies)} anomalies'})

@login_required
def generate_forecast(request):
    forecast = ForecastingService.forecast_expenses(request.user)
    return JsonResponse({'message': 'Forecast generated successfully'})

@login_required
def calculator(request):
    # Get recent calculations for the user
    recent_calculations = FinancialCalculation.objects.filter(user=request.user)[:10]
    
    context = {
        'recent_calculations': recent_calculations
    }
    
    return render(request, 'ai_features/calculator.html', context)

@login_required
def calculate(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        
        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)
        
        # Call the Gemini API for calculation
        calculation_result = GeminiService.financial_calculator(query)
        
        # Store the calculation in the database
        try:
            # Ensure insights is a string for database storage
            insights_json = json.dumps(calculation_result.get('insights', [])) if isinstance(calculation_result.get('insights', []), list) else calculation_result.get('insights', '[]')
            
            calculation = FinancialCalculation.objects.create(
                user=request.user,
                query=query,
                result=calculation_result.get('result', 'No result'),
                explanation=calculation_result.get('explanation', 'No explanation'),
                insights=insights_json
            )
            
            # Return the calculation results
            # Make sure we parse the insights properly
            insights = []
            if isinstance(calculation_result.get('insights', []), list):
                insights = calculation_result.get('insights', [])
            else:
                try:
                    insights = json.loads(calculation_result.get('insights', '[]'))
                except json.JSONDecodeError:
                    insights = [calculation_result.get('insights', 'No insights available')]
            
            return JsonResponse({
                'id': calculation.id,
                'result': calculation.result,
                'explanation': calculation.explanation,
                'insights': insights,
                'created_at': calculation.created_at.strftime('%Y-%m-%d %H:%M')
            })
            
        except Exception as e:
            import traceback
            print(f"Error processing calculation: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'error': f"Error processing calculation: {str(e)}",
                'details': str(calculation_result)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405) 