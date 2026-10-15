from django.contrib import admin

from .models import Order, Payment, Product, WebhookEvent


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_paise', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'amount_paise', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [PaymentInline]


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_type', 'received_at')