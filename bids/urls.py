from django.urls import path
from . import views

urlpatterns = [
    path('my-bids/', views.my_bids, name='my_bids'),
]