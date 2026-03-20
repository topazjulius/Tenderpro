from django.db import models
from django.contrib.auth.models import User
from tenders.models import Tender


class Bid(models.Model):

    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    proposal_document = models.FileField(
        upload_to="proposal_documents/",
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    is_winner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('vendor', 'tender')

    def __str__(self):
        return f"{self.vendor.username} - {self.tender.title}"