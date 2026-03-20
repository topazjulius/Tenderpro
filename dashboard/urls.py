from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_dashboard, name='vendor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vendor-performance/', views.vendor_performance, name='vendor_performance'),
]