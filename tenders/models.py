from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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

    # Optional document attachment (PDF, DOCX, etc.)
    document = models.FileField(
        upload_to="tender_documents/",
        null=True,
        blank=True
    )

    # Admin or staff who created the tender
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tenders_created"
    )

    # Timestamp when tender was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Winning bid (set after evaluation)
    awarded_bid = models.ForeignKey(
        'bids.Bid',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="awarded_tender"
    )

    def is_open(self):
        """
        Returns True if the tender deadline has not passed.
        """
        return timezone.now() < self.deadline

    def __str__(self):
        return f"{self.title} (Deadline: {self.deadline})"