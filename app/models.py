from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# ------------------------- STATE & CATEGORY CHOICES -------------------------
STATE_CHOICES = [
    ('Andaman & Nicobar Islands', 'Andaman & Nicobar Islands'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chandigarh', 'Chandigarh'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Dadra & Nagar Haveli', 'Dadra & Nagar Haveli'),
    ('Daman & Diu', 'Daman & Diu'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jammu & Kashmir', 'Jammu & Kashmir'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Puducherry', 'Puducherry'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttarakhand', 'Uttarakhand'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('West Bengal', 'West Bengal'),
]

CATEGORY_CHOICES = [
    ('MC', 'Mens Clothes'),  
    ('WC', 'Womens Clothes'), 
    ('KC', 'Kids Clothes'), 
    ('JW', 'Jewelry'), 
    ('SH', 'Shoes'),  
    ('BG', 'Bags'),  
    ('TY', 'Toys'),  
    ('AC', 'Accessories'),  
    ('EI', 'Electric Items'), 
]

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]

# ------------------------- PRODUCT MODEL -------------------------
class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='', blank=True)
    prodapp = models.TextField(default='', blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    product_image = models.ImageField(upload_to='product')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ------------------------- CUSTOMER MODEL -------------------------
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)  # Changed from IntegerField to CharField
    zipcode = models.CharField(max_length=10)  # Changed to CharField to allow leading zeros
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    created_at = models.DateTimeField(default=now) 
    
    @property
    def full_address(self):
        return f"{self.locality}, {self.city}, {self.state} - {self.zipcode}"
    
    def __str__(self):
        return self.name

# ------------------------- CART MODEL -------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price  
    
# ------------------------- PAYMENT MODEL -------------------------
class Payment(models.Model):
    PAYMENT_METHOD_COD = 'COD'
    PAYMENT_METHOD_ONLINE = 'Online'

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_COD, 'Cash on Delivery'),
        (PAYMENT_METHOD_ONLINE, 'Online Payment'),
    ]

    PENDING = 'Pending'
    SUCCESS = 'Success'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
    ]

    # order = models.OneToOneField(OrderPlaced, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_COD)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    date = models.DateTimeField(auto_now_add=True)

    # Card details (for online payment tracking)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_month = models.CharField(max_length=2, blank=True, null=True)
    expiry_year = models.CharField(max_length=2, blank=True, null=True)
    cvv = models.CharField(max_length=3, blank=True, null=True)

    def is_online_payment(self):
        """Check if payment is an online transaction."""
        return self.method == self.PAYMENT_METHOD_ONLINE

    def __str__(self):
        return f"Payment {self.id} - {self.status} ({self.method})"     

# ------------------------- ORDER MODEL -------------------------
class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders_as_customer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')


    
    
    
    # Shipping Address Linked Properly
    shipping_address = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_as_shipping_address'
    )

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

    @property
    def shipping_full_address(self):
        """Returns the full address of the shipping address if available."""
        return self.shipping_address.full_address if self.shipping_address else "No Address Provided"

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# ------------------------- PAYMENT RECEIPT MODEL -------------------------
class PaymentReceipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    receipt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for Payment {self.payment.id}"

# ------------------------- WISHLIST MODEL -------------------------
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist Item - {self.product.title} by {self.user.username}"
