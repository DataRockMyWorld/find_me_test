
from django.db import models
from django.conf import settings
from items.models import Item
from django.utils import timezone
import datetime

class Claim(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    lost_location = models.CharField(max_length=255)
    last_seen = models.DateTimeField(default=datetime.datetime.now)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')), default='pending')
    
    class Meta:
        unique_together = ('item', 'claimant')

    def __str__(self):
        return f"Claim by {self.claimant} on {self.item.title}"
