from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Product, Customer, Cart, Wishlist, OrderPlaced, Payment, PaymentReceipt
from django.contrib.auth.models import Group

# ------------------------- PRODUCT ADMIN -------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discounted_price', 'category', 'product_image']

# ------------------------- CUSTOMER ADMIN -------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'locality', 'city', 'state', 'zipcode']

# ------------------------- CART ADMIN -------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link', 'quantity']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)
    
    product_link.short_description = "Product"

# ------------------------- ORDER PLACED ADMIN -------------------------
@admin.register(OrderPlaced)
class OrderPlacedAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer_link', 'product_link', 'quantity', 'ordered_date', 'status', 'payment_status']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)

    def customer_link(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>', link, obj.customer.name)

    # Fetch payment status dynamically
    def payment_status(self, obj):
        return obj.payment.status if hasattr(obj, 'payment') else "Pending"
    
    payment_status.short_description = "Payment Status"

# ------------------------- PAYMENT ADMIN -------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'amount', 'method', 'status', 'date', 'card_number', 'expiry_month', 'expiry_year', 'cvv']

    def order_link(self, obj):
        link = reverse("admin:app_orderplaced_change", args=[obj.order.pk])
        return format_html('<a href="{}">Order {}</a>', link, obj.order.id)
    
    order_link.short_description = "Order"

# ------------------------- PAYMENT RECEIPT ADMIN -------------------------
@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_link', 'receipt_date']

    def payment_link(self, obj):
        link = reverse("admin:app_payment_change", args=[obj.payment.pk])
        return format_html('<a href="{}">Payment {}</a>', link, obj.payment.id)
    
    payment_link.short_description = "Payment"

# ------------------------- WISHLIST ADMIN -------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link']
    
    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)
    
    product_link.short_description = "Product"

# ------------------------- REMOVE GROUP FROM ADMIN -------------------------
admin.site.unregister(Group)
