from django.shortcuts import render, get_object_or_404, redirect  
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from dashboard.models import Notification, AuditLog  # ✅ ADDED AuditLog
from accounts.models import VendorProfile
from .models import Tender, Prequalification
from bids.models import Bid

# ===============================
# HOME (🔥 NEW - STATS)
# ===============================
def home(request):
    active_tenders = Tender.objects.filter(deadline__gt=timezone.now()).count()
    total_vendors = User.objects.filter(is_staff=False).count()
    awarded_tenders = Tender.objects.filter(awarded_bid__isnull=False).count()

    return render(request, "home.html", {
        "active_tenders": active_tenders,
        "total_vendors": total_vendors,
        "awarded_tenders": awarded_tenders,
    })

# ===============================
# LIST ALL TENDERS
# ===============================
def tender_list(request):

    query = request.GET.get('q')
    filter_status = request.GET.get('status')
    institution_id = request.GET.get('institution')
    category_id = request.GET.get('category')

    tenders = Tender.objects.select_related('institution', 'category').all().order_by('-id')

    if query:
        tenders = tenders.filter(title__icontains=query)

    if filter_status == "open":
        tenders = tenders.filter(deadline__gt=timezone.now())

    if institution_id:
        tenders = tenders.filter(institution_id=institution_id)

    if category_id:
        tenders = tenders.filter(category_id=category_id)

    from .models import Institution, Category
    institutions = Institution.objects.all()
    categories = Category.objects.all()

    return render(request, 'tenders/tender_list.html', {
        'tenders': tenders,
        'institutions': institutions,
        'categories': categories,
        'query': query,
        'filter_status': filter_status,
        'selected_institution': institution_id,
        'selected_category': category_id,
    })


# ===============================
# PREQUALIFICATION APPLY
# ===============================
@login_required
def apply_prequalification(request):

    if request.method == "POST":

        company_name = request.POST.get("company_name")
        category = request.POST.get("category")
        description = request.POST.get("description")
        document = request.FILES.get("document")

        if Prequalification.objects.filter(
            vendor=request.user,
            category=category
        ).exists():
            messages.warning(request, "⚠️ You have already applied for this category.")
            return redirect("tender_list")

        Prequalification.objects.create(
            vendor=request.user,
            company_name=company_name,
            category=category,
            description=description,
            document=document
        )

        # 🔔 Notification
        Notification.objects.create(
            user=request.user,
            message=f"Your prequalification application for '{category}' was submitted successfully."
        )

        # 📧 Email
        if request.user.email:
            send_mail(
                subject="Prequalification Application Received",
                message=f"""
Hello {request.user.username},

Your prequalification application has been received.

Category: {category}

TenderPro Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        messages.success(request, "✅ Application submitted successfully!")
        return redirect("tender_list")

    return render(request, "tenders/prequalification_form.html")


# ===============================
# TENDER DETAIL + BID
# ===============================
@login_required
def tender_detail(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    is_open = tender.deadline >= timezone.now()

    has_bid = Bid.objects.filter(
        tender=tender,
        vendor=request.user
    ).exists()

    if request.method == "POST":

     if request.user.is_staff:
        messages.error(request, "Admins cannot place bids.")
        return redirect('tender_detail', tender_id=tender.id)

    # ❌ BLOCK UNVERIFIED USERS
    try:
        profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        messages.error(request, "❌ Vendor profile not found.")
        return redirect('tender_list')

    if not profile.is_verified:
        messages.error(request, "❌ Your account is not verified.")
        return redirect('tender_list')

        if not is_open:
            messages.error(request, "This tender is already closed.")
            return redirect('tender_detail', tender_id=tender.id)

        if has_bid:
            messages.warning(request, "⚠️ You have already submitted a bid.")
            return redirect('tender_detail', tender_id=tender.id)

        amount = request.POST.get("amount")
        proposal_document = request.FILES.get("proposal_document")

        if not amount:
            messages.error(request, "Please enter a valid bid amount.")
            return redirect('tender_detail', tender_id=tender.id)

        # ✅ CREATE BID
        bid = Bid.objects.create(
            vendor=request.user,
            tender=tender,
            amount=amount,
            proposal_document=proposal_document
        )
        

        # 🔥 AUDIT LOG (NEW)
        AuditLog.objects.create(
            user=request.user,
            action="Placed bid",
            target=f"{tender.title} - KES {amount}"
        )

        # 🔔 Notification
        Notification.objects.create(
            user=request.user,
            message=f"You submitted a bid for '{tender.title}' (KES {amount})"
        )

        # 📧 Email
        if request.user.email:
            send_mail(
                subject="Bid Submitted Successfully",
                message=f"""
Hello {request.user.username},

Your bid has been successfully submitted.

Tender: {tender.title}
Amount: KES {amount}

Good luck!

TenderPro Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        messages.success(request, "✅ Bid submitted successfully!")
        return redirect('tender_detail', tender_id=tender.id)

    return render(request, 'tenders/tender_detail.html', {
        'tender': tender,
        'has_bid': has_bid,
        'is_open': is_open
    })


# ===============================
# ADMIN EVALUATION
# ===============================
@staff_member_required
def evaluate_tender(request, tender_id):

    tender = get_object_or_404(Tender, id=tender_id)

    bids = Bid.objects.filter(
        tender=tender
    ).select_related("vendor").order_by("amount")

    for index, bid in enumerate(bids, start=1):
        bid.rank = index

    return render(request, 'tenders/evaluate_tender.html', {
        'tender': tender,
        'bids': bids,
        'winner': tender.awarded_bid
    })


# ===============================
# AWARD BID (UPDATED 🔥)
# ===============================
@staff_member_required
def award_bid(request, tender_id, bid_id):

    tender = get_object_or_404(Tender, id=tender_id)
    winning_bid = get_object_or_404(Bid, id=bid_id, tender=tender)

    # ❌ CRITICAL FIX: Prevent self-award
    if winning_bid.vendor == request.user:
        messages.error(request, "❌ You cannot award a tender to yourself.")
        return redirect('evaluate_tender', tender_id=tender.id)

    tender.awarded_bid = winning_bid
    tender.save()

    # 🔥 AUDIT LOG (NEW)
    AuditLog.objects.create(
        user=request.user,
        action="Awarded tender",
        target=f"{tender.title} → {winning_bid.vendor.username}"
    )

    # 🔔 WINNER
    Notification.objects.create(
        user=winning_bid.vendor,
        message=f"🎉 You won the tender '{tender.title}'!"
    )

    # 📧 EMAIL WINNER
    if winning_bid.vendor.email:
        send_mail(
            subject="🎉 You Won the Tender!",
            message=f"""
Hello {winning_bid.vendor.username},

Congratulations!

You have been awarded:
"{tender.title}"

Your bid: KES {winning_bid.amount}

TenderPro System
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[winning_bid.vendor.email],
            fail_silently=True,
        )

    # ❌ LOSERS
    losing_bids = Bid.objects.filter(tender=tender).exclude(id=winning_bid.id)

    for bid in losing_bids:

        Notification.objects.create(
            user=bid.vendor,
            message=f"Your bid for '{tender.title}' was not selected."
        )

        if bid.vendor.email:
            send_mail(
                subject="Tender Result Notification",
                message=f"""
Hello {bid.vendor.username},

Your bid for "{tender.title}" was not selected.

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


# ===============================
# FILTER BY INSTITUTION
# ===============================
def tenders_by_institution(request, institution_id):

    from .models import Institution

    institution = get_object_or_404(Institution, id=institution_id)

    tenders = Tender.objects.filter(
        institution=institution
    ).select_related('institution', 'category').order_by('-id')

    return render(request, 'tenders/tenders_by_institution.html', {
        'institution': institution,
        'tenders': tenders
    })


# ===============================
# FILTER BY CATEGORY
# ===============================
def tenders_by_category(request, category_id):

    from .models import Category

    category = get_object_or_404(Category, id=category_id)

    tenders = Tender.objects.filter(
        category=category
    ).select_related('institution', 'category').order_by('-id')

    return render(request, 'tenders/tenders_by_category.html', {
        'category': category,
        'tenders': tenders
    })

# ===============================
# PUBLIC AWARDED TENDERS
# ===============================
def awarded_tenders(request):
    tenders = Tender.objects.filter(awarded_bid__isnull=False)

    return render(request, "tenders/awarded_tenders.html", {
        "tenders": tenders
    })