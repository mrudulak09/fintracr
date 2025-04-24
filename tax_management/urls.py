from django.urls import path
from . import views

app_name = 'tax_management'

urlpatterns = [
    path('dashboard/', views.tax_dashboard, name='dashboard'),
    path('profile/update/', views.update_tax_profile, name='update_profile'),
    path('calculate/<int:year>/', views.calculate_taxes, name='calculate_taxes'),
] 