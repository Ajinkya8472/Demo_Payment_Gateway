from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('buy/<slug:slug>/', views.checkout, name='checkout'),
    path('pay/<int:order_id>/', views.pay, name='pay'),
    path('payments/verify/', views.verify_payment, name='verify_payment'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('signup/', views.signup, name='signup'),
]