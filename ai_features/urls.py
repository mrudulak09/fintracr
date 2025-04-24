from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate-advice/', views.generate_advice, name='generate_advice'),
    path('detect-anomalies/', views.detect_anomalies, name='detect_anomalies'),
    path('generate-forecast/', views.generate_forecast, name='generate_forecast'),
    path('calculator/', views.calculator, name='calculator'),
    path('calculate/', views.calculate, name='calculate'),
] 