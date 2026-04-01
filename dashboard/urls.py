from django.urls import path
from . import views
from .views import notifications_view
from .views import vendor_dashboard
urlpatterns = [
    path('', views.vendor_dashboard, name='vendor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vendor-performance/', views.vendor_performance, name='vendor_performance'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path("notifications/", notifications_view, name="notifications"),
     path('', vendor_dashboard, name='dashboard'),
]