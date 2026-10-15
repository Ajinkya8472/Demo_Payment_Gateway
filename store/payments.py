import razorpay
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Order, Payment


def get_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def mark_paid(payment, razorpay_payment_id, razorpay_signature=''):
    """Mark an order as paid. Safe to call more than once (idempotent).

    The /verify endpoint calls this today; the Day 3 webhook will call it too.
    Returns True if this call did the update, False if it was already paid.
    """
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        if order.status == Order.Status.PAID:
            return False
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = Payment.Status.CAPTURED
        payment.save()
        order.status = Order.Status.PAID
        order.paid_at = timezone.now()
        order.save()
        return True