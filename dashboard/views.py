from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import vendor_required, admin_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from bids.models import Bid
from tenders.models import Tender
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import Notification


# ===============================
# HOME
# ===============================
def home(request):

    notifications = []
    unread_count = 0

    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

    return render(request, "home.html", {
        "notifications": notifications,
        "unread_count": unread_count,
    })


# ===============================
# VENDOR DASHBOARD (🔥 UPGRADED)
# ===============================
@login_required
@vendor_required
def vendor_dashboard(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    user = request.user

    # ===============================
    # 📊 STATS
    # ===============================
    user_bids = Bid.objects.filter(
        vendor=user
    ).select_related("tender")

    total_tenders = Tender.objects.count()
    total_bids = user_bids.count()

    open_tenders = Tender.objects.filter(
        deadline__gte=timezone.now()
    ).count()

    # ✅ FIXED: Only count awards WON by this user
    awards = Bid.objects.filter(
        vendor=user,
        tender__awarded_bid__vendor=user
    ).count()

    # ===============================
    # 📌 BID DATA + STATUS
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

    # ===============================
    # 📌 RECENT ACTIVITY (🔥 NEW)
    # ===============================
    recent_bids = user_bids.order_by('-submitted_at')[:5]

    return render(request, "dashboard/dashboard.html", {
        "bid_data": bid_data,
        "total_tenders": total_tenders,
        "total_bids": total_bids,
        "open_tenders": open_tenders,
        "awards": awards,
        "recent_bids": recent_bids,  # 🔥 NEW
    })


# ===============================
# ADMIN DASHBOARD
# ===============================
@admin_required
def admin_dashboard(request):

    now = timezone.now()

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

    open_tenders = Tender.objects.filter(
        deadline__gte=now
    ).count()

    closed_tenders = Tender.objects.filter(
        deadline__lt=now
    ).count()

    vendors = User.objects.filter(is_staff=False)

    vendor_names = []
    vendor_bids = []

    for vendor in vendors:
        count = Bid.objects.filter(vendor=vendor).count()
        vendor_names.append(vendor.username)
        vendor_bids.append(count)

    vendor_names_json = json.dumps(vendor_names)
    vendor_bids_json = json.dumps(vendor_bids)

    recent_tenders = Tender.objects.all().order_by('-id')[:5]

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

    return render(request, "dashboard/admin_dashboard.html", {
        "total_tenders": total_tenders,
        "total_vendors": total_vendors,
        "total_bids": total_bids,
        "awarded_tenders": awarded_tenders,
        "closing_soon": closing_soon,
        "vendor_names": vendor_names,
        "vendor_bids": vendor_bids,
        "vendor_names_json": vendor_names_json,
        "vendor_bids_json": vendor_bids_json,
        "open_tenders": open_tenders,
        "closed_tenders": closed_tenders,
        "recent_tenders": recent_tenders,
        "activity_feed": activity_feed,
        "now": now,
    })


# ===============================
# VENDOR PERFORMANCE
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

        win_rate = (wins / total_bids * 100) if total_bids > 0 else 0

        vendor_data.append({
            "vendor": vendor,
            "total_bids": total_bids,
            "wins": wins,
            "win_rate": round(win_rate, 1)
        })

    return render(request, "vendor_performance.html", {
        "vendor_data": vendor_data
    })


# ===============================
# 🔔 VIEW NOTIFICATIONS
# ===============================
@login_required
def notifications_view(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    notifications.update(is_read=True)

    return render(request, "dashboard/notifications.html", {
        "notifications": notifications
    })


# ===============================
# MARK NOTIFICATIONS READ
# ===============================
@login_required
def mark_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect(request.META.get('HTTP_REFERER', '/'))


# ===============================
# ABOUT PAGE
# ===============================
def about(request):
    return render(request, "about.html")


# ===============================
# CONTACT PAGE
# ===============================
def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        message_body = request.POST.get("message")

        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"""
Name: {name}
Email: {email}

Message:
{message_body}
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )

        messages.success(request, "✅ Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")