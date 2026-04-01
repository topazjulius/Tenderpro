from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ===============================
# INSTITUTION MODEL (Universities)
# ===============================
class Institution(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# ===============================
# CATEGORY MODEL (Tender Types)
# ===============================
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# ===============================
# TENDER MODEL
# ===============================
class Tender(models.Model):
    """
    Model representing a procurement tender.
    Vendors can view tenders and submit bids.
    """

    # Basic Tender Information
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Financial Information
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    # Deadline for bid submission
    deadline = models.DateTimeField()

    # ✅ Institution (NOW OPTIONAL)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="tenders",
        null=True,
        blank=True
    )

    # ✅ Category (NOW OPTIONAL)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="tenders",
        null=True,
        blank=True
    )

    # Optional document attachment
    document = models.FileField(
        upload_to="tender_documents/",
        null=True,
        blank=True
    )

    # Admin who created tender
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tenders_created"
    )

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    # Winning bid
    awarded_bid = models.ForeignKey(
        'bids.Bid',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awarded_tender"
    )

    # Check if tender is still open
    def is_open(self):
        return timezone.now() < self.deadline

    def __str__(self):
        # ✅ Safe display even if institution is empty
        if self.institution:
            return f"{self.title} ({self.institution})"
        return self.title


# ===============================
# PREQUALIFICATION MODEL
# ===============================
class Prequalification(models.Model):

    CATEGORY_CHOICES = [
        ("university", "University Suppliers"),
        ("government", "Government Vendors"),
        ("private", "Private Sector"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    vendor = models.ForeignKey(User, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    description = models.TextField()

    document = models.FileField(
        upload_to="prequal_docs/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.category}"