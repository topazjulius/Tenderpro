from django.urls import path
from . import views

urlpatterns = [
    path('my-bids/', views.my_bids, name='my_bids'),
    path('place/<int:tender_id>/', views.place_bid, name='place_bid'),
]