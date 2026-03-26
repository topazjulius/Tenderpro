from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Tender
from bids.models import Bid


# ===============================
# LIST ALL TENDERS
# ===============================
def tender_list(request):

    query = request.GET.get('q')
    filter_status = request.GET.get('status')

    tenders = Tender.objects.all().order_by('-id')

    # 🔍 Search
    if query:
        tenders = tenders.filter(title__icontains=query)

    # 🟢 Filter open tenders
    if filter_status == "open":
        tenders = tenders.filter(deadline__gt=timezone.now())

    return render(request, 'tenders/tender_list.html', {
        'tenders': tenders,
        'query': query
    })


# ===============================
# TENDER DETAIL + BID SUBMISSION (FIXED 🔥)
# ===============================
@login_required
def tender_detail(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    if request.method == "POST":

        # ❌ Prevent admin from bidding
        if request.user.is_staff:
            messages.error(request, "Admins cannot place bids.")
            return redirect('tender_detail', tender_id=tender.id)

        # ❌ Closed tender
        if tender.deadline < timezone.now():
            messages.error(request, "This tender is already closed.")
            return redirect('tender_detail', tender_id=tender.id)

        # ❌ Duplicate bid
        if Bid.objects.filter(vendor=request.user, tender=tender).exists():
            messages.warning(request, "⚠️ You have already submitted a bid for this tender.")
            return redirect('tender_detail', tender_id=tender.id)

        amount = request.POST.get("amount")
        proposal_document = request.FILES.get("proposal_document")

        # ❌ Validate amount
        if not amount:
            messages.error(request, "Please enter a valid bid amount.")
            return redirect('tender_detail', tender_id=tender.id)

        # ✅ CREATE BID
        Bid.objects.create(
            vendor=request.user,
            tender=tender,
            amount=amount,
            proposal_document=proposal_document
        )

        messages.success(request, "✅ Bid submitted successfully!")
        return redirect('tender_detail', tender_id=tender.id)

    return render(request, 'tenders/tender_detail.html', {
        'tender': tender
    })


# ===============================
# ADMIN BID EVALUATION PANEL (UPGRADED 🔥)
# ===============================
@staff_member_required
def evaluate_tender(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    bids = Bid.objects.filter(
        tender=tender
    ).select_related("vendor").order_by("amount")

    # 🧠 Add ranking dynamically
    for index, bid in enumerate(bids, start=1):
        bid.rank = index

    context = {
        'tender': tender,
        'bids': bids,
        'winner': tender.awarded_bid
    }

    return render(request, 'tenders/evaluate_tender.html', context)


# ===============================
# AWARD BID (UPGRADED 🔥)
# ===============================
@staff_member_required
def award_bid(request, tender_id, bid_id):

    tender = get_object_or_404(Tender, id=tender_id)
    winning_bid = get_object_or_404(Bid, id=bid_id, tender=tender)

    # 🏆 Assign winner
    tender.awarded_bid = winning_bid
    tender.save()

    # ===============================
    # 📧 EMAIL WINNER
    # ===============================
    if winning_bid.vendor.email:
        send_mail(
            subject="🎉 You Won the Tender!",
            message=f"""
Hello {winning_bid.vendor.username},

Congratulations!

You have been awarded the tender:
"{tender.title}"

Your bid: KES {winning_bid.amount}

Regards,
TenderPro System
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[winning_bid.vendor.email],
            fail_silently=True,
        )

    # ===============================
    # 📧 EMAIL LOSERS (PRO FEATURE 🔥)
    # ===============================
    losing_bids = Bid.objects.filter(tender=tender).exclude(id=winning_bid.id)

    for bid in losing_bids:
        if bid.vendor.email:
            send_mail(
                subject="Tender Result Notification",
                message=f"""
Hello {bid.vendor.username},

Thank you for participating in:
"{tender.title}"

Unfortunately, your bid was not selected.

Keep applying for future tenders.

Regards,
TenderPro System
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bid.vendor.email],
                fail_silently=True,
            )

    messages.success(request, "🏆 Tender awarded & notifications sent!")

    return redirect('evaluate_tender', tender_id=tender.id)


# ===============================
# VIEW ALL BIDS
# ===============================
@staff_member_required
def tender_bids(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    bids = Bid.objects.filter(
        tender=tender
    ).select_related("vendor").order_by("amount")

    return render(request, "tenders/tender_bids.html", {
        "tender": tender,
        "bids": bids
        
    })
