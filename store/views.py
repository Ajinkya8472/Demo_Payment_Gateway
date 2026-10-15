import razorpay
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SignupForm
from .models import Order, Payment, Product
from .payments import get_client, mark_paid


def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/home.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    # Filtering by user means someone else's order id gives a 404.
    order = get_object_or_404(Order.objects.select_related('product'), pk=pk, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
@require_POST
def checkout(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, 'Payments are not configured yet.')
        return redirect(product)

    try:
        # If the Razorpay call fails, the order insert rolls back too.
        with transaction.atomic():
            # The amount comes from the database, never from the browser.
            order = Order.objects.create(
                user=request.user, product=product, amount_paise=product.price_paise,
            )
            rz_order = get_client().order.create({
                'amount': order.amount_paise,
                'currency': 'INR',
                'receipt': f'order_{order.pk}',
            })
            Payment.objects.create(order=order, razorpay_order_id=rz_order['id'])
    except (razorpay.errors.BaseError, requests.exceptions.RequestException):
        messages.error(request, 'Could not start the payment. Please try again.')
        return redirect(product)

    return redirect('pay', order_id=order.pk)


@login_required
def pay(request, order_id):
    order = get_object_or_404(Order.objects.select_related('product'), pk=order_id, user=request.user)
    if order.status == Order.Status.PAID:
        return redirect('order_detail', pk=order.pk)
    payment = order.payments.first()  # newest first
    return render(request, 'store/checkout.html', {
        'order': order,
        'payment': payment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required
@require_POST
def verify_payment(request):
    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    # Only the logged-in user's own payments can be verified.
    payment = get_object_or_404(
        Payment.objects.select_related('order'),
        razorpay_order_id=razorpay_order_id,
        order__user=request.user,
    )

    try:
        get_client().utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, 'Payment could not be verified.')
        return redirect('order_detail', pk=payment.order_id)

    mark_paid(payment, razorpay_payment_id, razorpay_signature)
    return redirect('order_detail', pk=payment.order_id)