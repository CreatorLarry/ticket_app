from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser, User, PermissionsMixin
from django.utils import timezone


class OrganizerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_premium', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_premium') is not True:
            raise ValueError('Superuser must have is_premium=True.')

        return self.create_user(email, password, **extra_fields)


class Organizer(AbstractUser):
    username = None  # remove username field
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = OrganizerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # email

    def __str__(self):
        return self.email


# Event Model
class Event(models.Model):
    CATEGORY_CHOICES = [
        ("Music", "Music"),
        ("Tech", "Tech"),
        ("Sports", "Sports"),
        ("Food", "Food"),
        ("Business", "Business"),
        ("Education", "Education"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("trending", "Trending"),
        ("expired", "Expired"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    time = models.TimeField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    image = models.ImageField(upload_to="event_images/", default="default.jpg")
    # organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organized_events")
    contact = models.CharField(max_length=200, null=True, blank=True)
    organizer = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Upcoming")

    is_trending = models.BooleanField(default=False)  # 🔥 flag for trending

    def is_expired(self):
        return self.date < timezone.now().date()

    def is_upcoming(self):
        return self.date >= timezone.now().date()

    def __str__(self):
        return self.title


# Ticket Model
class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ("early_bird", "Early Bird"),
        ("regular", "Regular"),
        ("wave_1", "Wave 1"),
        ("wave_2", "Wave 2"),
        ("vip", "VIP"),
        ("vvip", "VVIP"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.event.title} - {self.get_category_display()}"


# Order Model
class Order(models.Model):
    PAYMENT_CHOICES = [
        ("mpesa", "M-Pesa"),
        ("card", "Card"),
        ("paypal", "PayPal"),
        ("bank", "Bank Transfer"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="orders")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    def __str__(self):
        return f"Order {self.id} - {self.event.title}"


# Event Dashboard Model
class EventDashboard(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Upcoming", "Upcoming"),
        ("Completed", "Completed"),
    ]

    title = models.CharField(max_length=255)
    date = models.DateField()
    tickets_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Upcoming")
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="event_dashboard")

    def __str__(self):
        return self.title
