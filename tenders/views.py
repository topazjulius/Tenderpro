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

    tenders = Tender.objects.all()

    # 🔍 Search
    if query:
        tenders = tenders.filter(title__icontains=query)

    # 🟢 Filter open tenders
    if filter_status == "open":
        tenders = tenders.filter(deadline__gt=timezone.now())

    context = {
        'tenders': tenders,
        'query': query
    }

    return render(request, 'tenders/tender_list.html', context)


# ===============================
# TENDER DETAIL + BID SUBMISSION
# ===============================
@login_required
def tender_detail(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)
    error = None

    if request.method == "POST":

        # ❌ Closed tender
        if tender.deadline < timezone.now():
            error = "This tender is already closed."

        # ❌ Duplicate bid
        elif Bid.objects.filter(vendor=request.user, tender=tender).exists():
            error = "You have already submitted a bid for this tender."

        else:
            amount = request.POST.get("amount")
            proposal_document = request.FILES.get("proposal_document")

            # ✅ Validate amount
            if not amount:
                error = "Please enter a valid bid amount."
            else:
                Bid.objects.create(
                    vendor=request.user,
                    tender=tender,
                    amount=amount,
                    proposal_document=proposal_document
                )

                messages.success(request, "Bid submitted successfully!")
                return redirect('tender_detail', tender_id=tender.id)

    context = {
        'tender': tender,
        'error': error
    }

    return render(request, 'tenders/tender_detail.html', context)


# ===============================
# ADMIN BID EVALUATION PANEL
# ===============================
@staff_member_required
def evaluate_tender(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    # 🔥 Sorted bids (lowest = best)
    bids = Bid.objects.filter(
        tender=tender
    ).select_related("vendor").order_by("amount")

    context = {
        'tender': tender,
        'bids': bids,
        'winner': tender.awarded_bid
    }

    return render(request, 'tenders/evaluate_tender.html', context)


# ===============================
# AWARD BID (ADMIN + EMAIL SYSTEM)
# ===============================
@staff_member_required
def award_bid(request, tender_id, bid_id):

    tender = get_object_or_404(Tender, id=tender_id)
    winning_bid = get_object_or_404(Bid, id=bid_id, tender=tender)

    # 🏆 Assign winner
    tender.awarded_bid = winning_bid
    tender.save()

    # ===============================
    # 📧 EMAIL TO WINNER
    # ===============================
    if winning_bid.vendor.email:
        send_mail(
            subject="🎉 You Won the Tender!",
            message=f"""
Hello {winning_bid.vendor.username},

Congratulations! 🎉

You have been awarded the tender:
"{tender.title}"

Your bid: {winning_bid.amount}

Log in to your dashboard for more details.

Regards,
Tender Management System
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[winning_bid.vendor.email],
            fail_silently=True,
        )

    # ===============================
    # 📧 EMAIL TO LOSERS (OPTIONAL UPGRADE 🔥)
    # ===============================
    losing_bids = Bid.objects.filter(tender=tender).exclude(id=winning_bid.id)

    for bid in losing_bids:
        if bid.vendor.email:
            send_mail(
                subject="Tender Result Notification",
                message=f"""
Hello {bid.vendor.username},

Thank you for participating in the tender:
"{tender.title}"

Unfortunately, your bid was not selected this time.

We encourage you to apply for future tenders.

Best regards,
Tender Management System
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bid.vendor.email],
                fail_silently=True,
            )

    messages.success(request, "Tender awarded and notifications sent!")

    return redirect('evaluate_tender', tender_id=tender.id)


# ===============================
# VIEW ALL BIDS FOR A TENDER
# ===============================
@staff_member_required
def tender_bids(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    bids = Bid.objects.filter(
        tender=tender
    ).select_related("vendor").order_by("amount")

    context = {
        "tender": tender,
        "bids": bids
    }

    return render(request, "tenders/tender_bids.html", context)