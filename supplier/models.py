from django.db import models
from django.contrib.auth.models import User
from manufacturer.models import QuoteRequest

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    business_type = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20)
    key_services = models.TextField()
    wallet_address = models.CharField(max_length=42, blank=True, null=True)
    
    
    def __str__(self):
        return self.company_name
    
class Bid(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    quote = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in days")
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='submitted')
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('deposited', 'Deposit Received'),
        ('released', 'Payment Released'),
        ('disputed', 'Disputed'),
    ]
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    transaction_hash = models.CharField(max_length=66, blank=True, null=True)

    def __str__(self):
        return f"Bid for {self.quote.product} by {self.supplier.company_name}"