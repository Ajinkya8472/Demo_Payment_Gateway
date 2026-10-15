from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('buy/<slug:slug>/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('signup/', views.signup, name='signup'),
]