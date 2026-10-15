from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SignupForm
from .models import Order, Product


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
@require_POST
def checkout(request, slug):
    # DAY 2: create Order + Razorpay order here (amount from DB, never from the browser).
    product = get_object_or_404(Product, slug=slug, is_active=True)
    messages.info(request, 'Checkout is coming on Day 2.')
    return redirect(product)