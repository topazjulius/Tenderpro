from django.urls import path
from . import views

urlpatterns = [

    # View all tenders
    path('', views.tender_list, name='tender_list'),

    # View tender details + submit bid
    path('<int:tender_id>/', views.tender_detail, name='tender_detail'),

    # Admin evaluates bids
    path('evaluate/<int:tender_id>/', views.evaluate_tender, name='evaluate_tender'),

    # Admin awards winning bid
    path('award/<int:tender_id>/<int:bid_id>/', views.award_bid, name='award_bid'),

path('bids/<int:tender_id>/', views.tender_bids, name='tender_bids'),
]