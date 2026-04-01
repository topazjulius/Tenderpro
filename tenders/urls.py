from django.urls import path
from . import views

urlpatterns = [

    # ===============================
    # LIST ALL TENDERS
    # ===============================
    path('', views.tender_list, name='tender_list'),

    # ===============================
    # ADMIN ACTIONS (PUT FIRST ✅)
    # ===============================
    path('evaluate/<int:tender_id>/', views.evaluate_tender, name='evaluate_tender'),
    path('award/<int:tender_id>/<int:bid_id>/', views.award_bid, name='award_bid'),
    path('bids/<int:tender_id>/', views.tender_bids, name='tender_bids'),

    # ===============================
    # TENDER DETAIL (PUT LAST ⚠️)
    # ===============================
    path('<int:tender_id>/', views.tender_detail, name='tender_detail'),

    path('prequalification/apply/', views.apply_prequalification, name='apply_prequalification'),

    path('institution/<int:institution_id>/', views.tenders_by_institution, name='tenders_by_institution'),

path('category/<int:category_id>/', views.tenders_by_category, name='tenders_by_category'),

path('awarded/', views.awarded_tenders, name='awarded_tenders'),
]