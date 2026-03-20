from django.shortcuts import render
from .models import Bid

def my_bids(request):
    bids = Bid.objects.filter(vendor=request.user)
    return render(request, 'bids/my_bids.html', {'bids': bids})