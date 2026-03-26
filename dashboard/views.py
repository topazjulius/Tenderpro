from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from accounts.decorators import vendor_required, admin_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from bids.models import Bid
from tenders.models import Tender
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


# ===============================
# HOME
# ===============================
def home(request):
   context = {
        "total_tenders": Tender.objects.filter(deadline__gte=timezone.now()).count(),
        "total_vendors": User.objects.filter(is_staff=False).count(),
        "total_awards": Tender.objects.filter(awarded_bid__isnull=False).count(),
    }
   return render(request, "home.html", context)


# ===============================
# VENDOR DASHBOARD (USER SIDE)
# ===============================
@login_required
@vendor_required
def vendor_dashboard(request):

    # Redirect admin to admin dashboard
    if request.user.is_staff:
        return redirect("admin_dashboard")

    user_bids = Bid.objects.filter(
        vendor=request.user
    ).select_related("tender")

    # ===============================
    # KPI STATS (FIXED ✅)
    # ===============================
    total_tenders = Tender.objects.count()
    total_bids = user_bids.count()
    open_tenders = Tender.objects.filter(
        deadline__gte=timezone.now()
    ).count()

    awarded_tenders = Tender.objects.filter(
        awarded_bid__isnull=False
    ).count()

    # ===============================
    # BID DATA
    # ===============================
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

    # ✅ FIX: Added KPI data to context
    context = {
        "bid_data": bid_data,
        "total_tenders": total_tenders,
        "total_bids": total_bids,
        "open_tenders": open_tenders,
        "awarded_tenders": awarded_tenders,
    }

    return render(request, "dashboard/dashboard.html", context)


# ===============================
# ADMIN DASHBOARD (ENTERPRISE UI)
# ===============================
@admin_required
def admin_dashboard(request):

    now = timezone.now()

    # ===============================
    # KPI STATS
    # ===============================
    total_tenders = Tender.objects.count()
    total_vendors = User.objects.filter(is_staff=False).count()
    total_bids = Bid.objects.count()

    awarded_tenders = Tender.objects.filter(
        awarded_bid__isnull=False
    ).count()

    closing_soon = Tender.objects.filter(
        deadline__lte=now + timedelta(days=3),
        deadline__gte=now
    ).count()

    # ===============================
    # TENDER STATUS
    # ===============================
    open_tenders = Tender.objects.filter(
        deadline__gte=now
    ).count()

    closed_tenders = Tender.objects.filter(
        deadline__lt=now
    ).count()

    # ===============================
    # VENDOR PERFORMANCE (CHART)
    # ===============================
    vendors = User.objects.filter(is_staff=False)

    vendor_names = []
    vendor_bids = []

    for vendor in vendors:
        count = Bid.objects.filter(vendor=vendor).count()

        vendor_names.append(vendor.username)
        vendor_bids.append(count)

    # ===============================
    # RECENT TENDERS
    # ===============================
    recent_tenders = Tender.objects.all().order_by('-id')[:5]

    # ===============================
    # RECENT ACTIVITY
    # ===============================
    recent_bids = Bid.objects.select_related(
        "vendor", "tender"
    ).order_by('-submitted_at')[:5]

    activity_feed = []

    for bid in recent_bids:
        activity_feed.append({
            "user": bid.vendor.username,
            "action": f"placed a bid on {bid.tender.title}",
            "time": bid.submitted_at
        })

    # ===============================
    # CONTEXT
    # ===============================
    context = {
        # KPIs
        "total_tenders": total_tenders,
        "total_vendors": total_vendors,
        "total_bids": total_bids,
        "awarded_tenders": awarded_tenders,
        "closing_soon": closing_soon,

        # Charts
        "vendor_names": vendor_names,
        "vendor_bids": vendor_bids,
        "open_tenders": open_tenders,
        "closed_tenders": closed_tenders,

        # Tables
        "recent_tenders": recent_tenders,

        # Activity
        "activity_feed": activity_feed,

        # Time
        "now": now,
    }

    return render(request, "dashboard/admin_dashboard.html", context)


# ===============================
# VENDOR PERFORMANCE DASHBOARD
# ===============================
@admin_required
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

# ===============================
# ABOUT PAGE
# ===============================
def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")