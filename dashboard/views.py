from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone

from bids.models import Bid
from tenders.models import Tender


# ===============================
# HOME
# ===============================
def home(request):
    return render(request, "home.html")


# ===============================
# VENDOR DASHBOARD
# ===============================
@login_required
def vendor_dashboard(request):

    # Ensure user is a vendor
    if not hasattr(request.user, "vendorprofile"):
        return redirect("home")

    user_bids = Bid.objects.filter(
        vendor=request.user
    ).select_related("tender")

    bid_data = []

    for bid in user_bids:

        tender = bid.tender

        if tender.awarded_bid == bid:
            status = "WON"
        elif tender.awarded_bid is not None:
            status = "LOST"
        else:
            status = "PENDING"

        bid_data.append({
            "tender": tender,
            "amount": bid.amount,
            "status": status,
           "submitted_at": bid.submitted_at
        })

    context = {
        "bid_data": bid_data
    }

    return render(request, "dashboard/dashboard.html", context)


# ===============================
# ADMIN DASHBOARD
# ===============================
@staff_member_required
def admin_dashboard(request):

    total_tenders = Tender.objects.count()

    open_tenders = Tender.objects.filter(
        deadline__gte=timezone.now()
    ).count()

    closed_tenders = Tender.objects.filter(
        deadline__lt=timezone.now()
    ).count()

    total_bids = Bid.objects.count()

    awarded_tenders = Tender.objects.filter(
        awarded_bid__isnull=False
    ).count()

    total_vendors = User.objects.filter(
        is_staff=False
    ).count()

    context = {
        "total_tenders": total_tenders,
        "open_tenders": open_tenders,
        "closed_tenders": closed_tenders,
        "total_bids": total_bids,
        "awarded_tenders": awarded_tenders,
        "total_vendors": total_vendors
    }

    return render(request, "dashboard/admin_dashboard.html", context)


# ===============================
# VENDOR PERFORMANCE DASHBOARD
# ===============================
@staff_member_required
def vendor_performance(request):

    vendors = User.objects.filter(is_staff=False)

    vendor_data = []

    for vendor in vendors:

        total_bids = Bid.objects.filter(vendor=vendor).count()

        wins = Bid.objects.filter(
            vendor=vendor,
            tender__awarded_bid__vendor=vendor
        ).count()

        win_rate = 0
        if total_bids > 0:
            win_rate = (wins / total_bids) * 100

        vendor_data.append({
            "vendor": vendor,
            "total_bids": total_bids,
            "wins": wins,
            "win_rate": round(win_rate, 1)
        })

    context = {
        "vendor_data": vendor_data
    }

    return render(request, "vendor_performance.html", context)