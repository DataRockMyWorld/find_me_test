from django.db import models
from django.utils import timezone
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = (
        ('lost', 'Lost'),
        ('found', 'Found'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='lost')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='item_images/', blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    def has_pending_claims(self):
        return self.claims.filter(status='pending').exists()

    def has_approved_claim(self):
        return self.claims.filter(status='approved').exists()


    def __str__(self):
        return self.title


class Notification(models.Model):
    TYPE_CHOICES = (
        ('claim_made', 'Claim Made'),
        ('claim_approved', 'Claim Approved'),
        ('claim_rejected', 'Claim Rejected'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.get_type_display()}"
