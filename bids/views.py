from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Bid
from tenders.models import Tender


# ===============================
# VIEW: MY BIDS (VENDOR)
# ===============================
@login_required
def my_bids(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    bids = Bid.objects.filter(
        vendor=request.user
    ).select_related('tender').order_by('-submitted_at')

    context = {
        'bids': bids
    }

    return render(request, 'bids/my_bids.html', context)


# ===============================
# VIEW: PLACE BID
# ===============================
@login_required
def place_bid(request, tender_id):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    tender = get_object_or_404(Tender, id=tender_id)

    # ❌ Prevent bidding on closed tenders
    if tender.deadline < timezone.now():
        messages.error(request, "❌ This tender is already closed.")
        return redirect('/tenders/')

    if request.method == "POST":
        amount = request.POST.get('amount')

        # ❌ Validate amount
        if not amount:
            messages.error(request, "Please enter a bid amount.")
            return redirect(request.path)

        # ❌ Prevent duplicate bids
        if Bid.objects.filter(vendor=request.user, tender=tender).exists():
            messages.warning(request, "⚠️ You have already placed a bid on this tender.")
            return redirect('/bids/my-bids/')

        # ✅ Create bid
        Bid.objects.create(
            vendor=request.user,
            tender=tender,
            amount=amount
        )

        messages.success(request, "✅ Bid submitted successfully!")
        return redirect('/bids/my-bids/')

    return render(request, 'bids/place_bid.html', {'tender': tender})