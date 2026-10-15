from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    tagline = models.CharField(max_length=160)
    description = models.TextField()
    # Stored in paise (INR * 100) to avoid float rounding. Razorpay also uses paise.
    price_paise = models.PositiveIntegerField()
    accent_color = models.CharField(max_length=7, default='#3A5BFF', help_text='Hex colour for the product tile')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def price_rupees(self):
        return self.price_paise / 100

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    # Snapshot of the price at purchase time, so later price edits never change old orders.
    amount_paise = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def amount_rupees(self):
        return self.amount_paise / 100

    def __str__(self):
        return f'Order #{self.pk} ({self.status})'


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        CAPTURED = 'captured', 'Captured'
        FAILED = 'failed', 'Failed'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=64, unique=True)
    razorpay_payment_id = models.CharField(max_length=64, blank=True)
    razorpay_signature = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # At most one captured payment per order, enforced by the database.
            models.UniqueConstraint(
                fields=['order'],
                condition=models.Q(status='captured'),
                name='one_captured_payment_per_order',
            ),
        ]

    def __str__(self):
        return self.razorpay_order_id


class WebhookEvent(models.Model):
    """Every webhook we receive. The unique event_id makes processing idempotent."""
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=60)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.event_type} {self.event_id}'