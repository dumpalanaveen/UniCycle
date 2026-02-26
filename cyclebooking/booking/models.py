from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    roll_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Cycle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Under Maintenance'),
    ]
    name = models.CharField(max_length=100)
    cycle_id = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='cycles/', blank=True, null=True)
    gear_type = models.CharField(max_length=50, default='Single Speed')
    color = models.CharField(max_length=50)
    condition = models.CharField(max_length=50, default='Good')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.cycle_id})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    unlock_pin = models.CharField(max_length=4, blank=True)
    payment_reference = models.CharField(max_length=50, blank=True)
    qr_data = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    # Return tracking
    returned_at = models.DateTimeField(null=True, blank=True)
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    COST_PER_10_MIN = 3 

    def calculate_cost(self):
        return round((self.duration_minutes / 10) * self.COST_PER_10_MIN, 2)

    def generate_pin(self):
        return ''.join(random.choices(string.digits, k=4))

    def generate_payment_ref(self):
        return 'PAY' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def save(self, *args, **kwargs):
        if not self.total_cost:
            self.total_cost = self.calculate_cost()
        if not self.unlock_pin:
            self.unlock_pin = self.generate_pin()
        if not self.payment_reference:
            self.payment_reference = self.generate_payment_ref()
        if not self.qr_data:
            self.qr_data = (
                f"upi://pay?pa=unicycle@upi"
                f"&pn=UniCycle+University"
                f"&am={self.total_cost}"
                f"&tn={self.payment_reference}"
                f"&cu=INR"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.cycle.name}"
