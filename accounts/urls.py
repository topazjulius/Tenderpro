from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_vendor, name='register'),
    path('login/', views.login_vendor, name='login'),
    path('logout/', views.logout_vendor, name='logout'),
]