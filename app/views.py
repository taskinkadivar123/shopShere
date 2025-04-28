from django.shortcuts import render,redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from .models import *
from django.db.models import Count
from .forms import CustomerRegisterForm,CustomerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .models import Cart, Customer, Product,Wishlist,User,OrderPlaced
from django.contrib import messages
from .forms import ProductForm,forms
from .forms import  AddressForm
from datetime import datetime
from .forms import ContactForm
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa





from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:  # Check if the user is an admin
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')  # Redirect to dashboard or next URL
                return redirect(next_url)
            else:
                messages.error(request, "You do not have permission to access the admin area.")
                return redirect('admin_login')
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'app/admin_login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.is_staff = True  # Set the user as admin
                user.save()
                messages.success(request, "Admin registered successfully.")
                return redirect('admin_login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'app/admin_register.html')

# @login_required
# def dashboard(request):
#     # Check if the user is an admin (is_staff=True)
#     if not request.user.is_staff:
#         return HttpResponse("Unauthorized access", status=403)  # Forbidden if not admin

#     # Fetch data for the admin dashboard
#     users = User.objects.all()
#     products = Product.objects.all()
#     carts = Cart.objects.all()
#     payments = Payment.objects.all()
#     wishlists = Wishlist.objects.all()
#     orders = OrderPlaced.objects.all()

#     # Count users created per month
#     user_stats_month = User.objects.annotate(month=Count('date_joined__month')).values('month').annotate(count=Count('id')).order_by('month')
    
#     # Prepare data for monthly chart
#     months = []
#     user_count_month = []
#     for stat in user_stats_month:
#         month = datetime(stat['month'], 1, 1).strftime('%B')  # Convert month to month name
#         months.append(month)
#         user_count_month.append(stat['count'])

#     # Count users created per day
#     user_stats_day = User.objects.annotate(day=Count('date_joined__date')).values('date_joined__date').annotate(count=Count('id')).order_by('date_joined__date')

#     # Prepare data for daily chart
#     days = []
#     user_count_day = []
#     for stat in user_stats_day:
#         day = stat['date_joined__date'].strftime('%Y-%m-%d')  # Convert date to string (YYYY-MM-DD)
#         days.append(day)
#         user_count_day.append(stat['count'])

#     # Render the dashboard page with all the necessary context
#     return render(request, 'app/admin_dashboard.html', {
#         'users': users,
#         'products': products,
#         'carts': carts,
#         'payments': payments,
#         'wishlists': wishlists,
#         'orders': orders,
#         'months': months,
#         'user_count_month': user_count_month,
#         'days': days,
#         'user_count_day': user_count_day,
#     })

from django.db.models import Sum, F, DecimalField
from django.utils.dateparse import parse_date
from django.shortcuts import render
from datetime import datetime
from .models import OrderPlaced, Customer, Product  # <== Added Product model
from django.contrib.auth.models import User

def dashboard(request):
    # Date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        from_date = parse_date(start_date)
        to_date = parse_date(end_date)
    else:
        from_date = datetime.today().replace(day=1)
        to_date = datetime.today()

    orders = OrderPlaced.objects.filter(ordered_date__range=[from_date, to_date])

    # Revenue
    revenue = orders.aggregate(
        total=Sum(F('quantity') * F('product__discounted_price'), output_field=DecimalField())
    )['total'] or 0

    # New customers
    new_customers = Customer.objects.filter(user__date_joined__range=[from_date, to_date]).count()

    # New orders
    new_orders = orders.count()

    # Latest 5 users (registered anytime)
    latest_users = User.objects.order_by('-date_joined')[:5]

    # Latest 5 orders (placed anytime)
    latest_orders = OrderPlaced.objects.order_by('-ordered_date')[:5]

    # Extra Stats
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    pending_orders = OrderPlaced.objects.filter(status='Pending').count()

    context = {
        'revenue': revenue,
        'new_customers': new_customers,
        'new_orders': new_orders,
        'latest_users': latest_users,
        'latest_orders': latest_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'pending_orders': pending_orders,
    }

    return render(request, 'app/admin_dashboard.html', context)

from .models import User

def dashboard_users(request):
    # Capture the search query from the GET request (if present)
    search_query = request.GET.get('q', '')
    
    # Filter users if there is a search query, else return all users
    if search_query:
        user_list = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        user_list = User.objects.all()

    # Paginate the queryset, 8 users per page
    paginator = Paginator(user_list, 8)
    
    # Get the current page number from the request (defaults to 1 if no page is specified)
    page_number = request.GET.get('page', 1)

    # Get the users for the current page
    page_obj = paginator.get_page(page_number)

    # Pass the page object and search query to the template
    return render(request, 'app/admin_dashboard_users.html', {
        'users': page_obj,
        'search_query': search_query
    })

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Get form data
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Add a success message
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('dashboard_users')

    return render(request, 'app/admin_edit_user.html', {'user': user})

def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_name = user.username
        user.delete()
        
        # Add a success message
        messages.success(request, f'User {user_name} deleted successfully.')
        
        return redirect('dashboard_users')  # Redirect back to the users dashboard
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard_users')

def dashboard_products(request):
    search_query = request.GET.get('q', '')
    
    # If there's a search query, filter products by title or category
    if search_query:
        products_list = Product.objects.filter(title__icontains=search_query) | Product.objects.filter(category__icontains=search_query)
    else:
        products_list = Product.objects.all()

    # For front-end new arrivals section, we'll show the 8 most recent products
    new_arrivals = products_list.order_by('-created_at')[:8]  # Modify `created_at` to whatever field is relevant

    paginator = Paginator(products_list, 8)  # Show 8 products per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'app/admin_dashboard_products.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'new_arrivals': new_arrivals
    })
    
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('dashboard_products')  # Redirect to the products list page
    else:
        form = ProductForm()

    return render(request, 'app/admin_add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.title}" updated successfully!')
            return redirect('dashboard_products')  # Redirect to the products list page
    else:
        form = ProductForm(instance=product)

    return render(request, 'app/admin_edit_product.html', {'form': form})

def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product_name = product.title
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
    
    return redirect('dashboard_products')


# def dashboard_carts(request):
#     # Fetch all carts
#     carts = Cart.objects.all()

#     # Set up pagination
#     paginator = Paginator(carts, 8)  # 10 carts per page
#     page_number = request.GET.get('page')  # Get the current page number
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'app/admin_dashboard_carts.html', {'carts': page_obj})
def dashboard_carts(request):
    # Get the search query from the GET request, if any
    search_query = request.GET.get('q', '')

    # Filter the carts based on the search query
    if search_query:
        carts = Cart.objects.filter(
            user__username__icontains=search_query
        )  # Search for carts by username (you can also add product or other fields)
    else:
        carts = Cart.objects.all()

    # Set up pagination
    paginator = Paginator(carts, 8)  # 8 carts per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/admin_dashboard_carts.html', {
        'carts': page_obj,
        'search_query': search_query  # Pass search query to the template
    })

def delete_cart_item(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    cart_item.delete()
    return redirect('dashboard_carts')


def dashboard_payments(request):
    query = request.GET.get('q', '')

    # Fetch related orders and users
    payments = Payment.objects.prefetch_related('orders__user')

    if query:
        payments = payments.filter(
            Q(orders__id__icontains=query) |
            Q(orders__user__username__icontains=query)
        ).distinct()

    paginator = Paginator(payments.order_by('-date'), 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app/admin_dashboard_payments.html', {
        'payments': page_obj
    })
    
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    messages.success(request, "Payment deleted successfully.")
    return redirect('dashboard_payments')
  

# def dashboard_wishlists(request):
#     wishlists = Wishlist.objects.all()  # Get all wishlist items
#     paginator = Paginator(wishlists, 10)  # Paginate by 10 items per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # Handle deletion of wishlist item
#     if 'delete_wishlist' in request.GET:
#         wishlist_id = request.GET.get('delete_wishlist')
#         try:
#             wishlist = Wishlist.objects.get(id=wishlist_id)
#             wishlist.delete()
#             messages.success(request, "Wishlist item deleted successfully.")
#         except Wishlist.DoesNotExist:
#             messages.error(request, "Wishlist item not found.")
#         return redirect('dashboard_wishlists')

#     return render(request, 'app/admin_dashboard_wishlists.html', {'wishlists': page_obj})

def dashboard_wishlists(request):
    # Get the search query from the GET request, if present
    search_query = request.GET.get('q', '')

    # Filter the wishlists based on the search query, if present
    if search_query:
        wishlists = Wishlist.objects.filter(
            user__username__icontains=search_query
        ) | Wishlist.objects.filter(
            product__title__icontains=search_query
        )
    else:
        wishlists = Wishlist.objects.all()

    # Paginate the filtered queryset
    paginator = Paginator(wishlists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle deletion of wishlist item
    if 'delete_wishlist' in request.GET:
        wishlist_id = request.GET.get('delete_wishlist')
        try:
            wishlist = Wishlist.objects.get(id=wishlist_id)
            wishlist.delete()
            messages.success(request, "Wishlist item deleted successfully.")
        except Wishlist.DoesNotExist:
            messages.error(request, "Wishlist item not found.")
        return redirect('dashboard_wishlists')

    return render(request, 'app/admin_dashboard_wishlists.html', {
        'wishlists': page_obj,
        'search_query': search_query
    })


def dashboard_orders(request):
    query = request.GET.get('q')
    orders = OrderPlaced.objects.select_related('user', 'product', 'payment')

    if query:
        orders = orders.filter(
            Q(user__username__icontains=query) |
            Q(product__name__icontains=query)
        )

    orders = orders.order_by('-ordered_date')

    # Pagination: show 10 orders per page
    paginator = Paginator(orders, 6)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    return render(request, 'app/admin_dashboard_orders.html', {'orders': orders_page})






from .forms import EditOrderForm  # You need to create this form
from django.contrib import messages

def edit_order(request, pk):
    order = get_object_or_404(OrderPlaced, pk=pk)

    if request.method == 'POST':
        form = EditOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order updated successfully.")
            return redirect('dashboard_orders')
    else:
        form = EditOrderForm(instance=order)

    return render(request, 'app/admin_edit_orders.html', {'form': form, 'order': order})

def delete_order(request, pk):
    order = get_object_or_404(OrderPlaced, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Order deleted successfully.")
        return redirect('dashboard_orders')
    return redirect('dashboard_orders')







# Create your views here.
# @login_required
# def home(request):
#     totalitem = 0
#     wishitem = 0 
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#         wishitem = len(Wishlist.objects.filter(user=request.user))
#     return render(request,'app/home.html',locals())
@login_required
def home(request):
    totalitem = 0
    wishitem = 0
    
    # Calculate total items in the cart and wishlist items for the authenticated user
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
    
    # Fetch the 8 latest products (new arrivals)
    new_arrivals = Product.objects.all().order_by('-created_at')[:8]  # Modify `created_at` based on your model

    # Pass everything to the template
    return render(request, 'app/home.html', {
        'totalitem': totalitem,
        'wishitem': wishitem,
        'new_arrivals': new_arrivals
    })

@login_required
def about(request):
    totalitem = 0
    wishitem = 0 
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/about.html',locals())

@login_required
def blog(request):
    totalitem = 0
    wishitem = 0 
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/blog.html',locals())

# @login_required
# def contact(request):
#     totalitem = 0
#     wishitem = 0 
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#         wishitem = len(Wishlist.objects.filter(user=request.user))
#     return render(request,'app/contact.html',locals())

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
    
@method_decorator(login_required,name='dispatch')    
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        totalitem = 0
        wishitem = 0
        Wishlist
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())
     
@method_decorator(login_required,name='dispatch')     
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,"app/productdetail.html",locals())      
    
  
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegisterForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegisterForm(request.POST)  
        if form.is_valid():
            form.save()
            messages.success(request,"User Register Succesfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,'app/customerregistration.html',locals())   





@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        wishitem = 0 
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form': form})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            # Check if user is authenticated
            if user.is_authenticated:
                reg = Customer(user=user, name=name, locality=locality, city=city,
                               mobile=mobile, state=state, zipcode=zipcode)
                reg.save()
                messages.success(request, "Congratulations! Profile saved successfully.")
            else:
                messages.warning(request, "You must be logged in to save your profile.")
        else:
            messages.warning(request, "Invalid data")
        return render(request, 'app/profile.html', {'form': form})
    

# @method_decorator(login_required,name='dispatch')
@login_required
def addresss(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to view your addresses.")
        return redirect('profile')  # Redirect to profile or login page

    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'add': add})


from django.contrib.auth.views import PasswordResetDoneView

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'app/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.POST.get('email')  # Pass the email entered by the user
        return context

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self, request, pk):
        add = get_object_or_404(Customer, pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/updateAddress.html', {'form': form, 'request': request})

    def post(self, request, pk):
        add = get_object_or_404(Customer, pk=pk)  # Get the existing customer object
        form = CustomerProfileForm(request.POST, instance=add)  # Pass the instance to the form

        if form.is_valid():
            form.save()  # This will update the existing instance
            messages.success(request, "Congratulations! Profile updated successfully.")
            return redirect("address")
        else:
            messages.warning(request, "Invalid data")    

        return render(request, 'app/updateAddress.html', {'form': form, 'request': request})  # Render the form with errors if invalid
    
@login_required    
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

@login_required
def show_cart(request):
    user = request.user
    totalitem = 0
    wishitem = 0

    if user.is_authenticated:
        # Fetch cart items
        cart = Cart.objects.filter(user=user)

        # Remove items from cart that are already ordered with successful payment
        for item in cart:
            already_ordered = OrderPlaced.objects.filter(
                user=user, product=item.product, payment__status='Success'
            ).exists()
            if already_ordered:
                item.delete()  # Remove it from cart

        # Fetch updated cart after removal
        cart = Cart.objects.filter(user=user)

        # Calculate amount
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        totalamount = amount + 40  # shipping
        totalitem = len(cart)
        wishitem = len(Wishlist.objects.filter(user=user))
    else:
        cart = []
        totalamount = 0
        totalitem = 0

    return render(request, 'app/addtocart.html', {
        'cart': cart,
        'totalamount': totalamount,
        'totalitem': totalitem,
        'wishitem': wishitem,
    })


# @login_required
# def show_cart(request):
#     user = request.user
#     totalitem = 0
#     wishitem = 0 
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#         wishitem = len(Wishlist.objects.filter(user=request.user))
#     # Check if user is authenticated
#     if user.is_authenticated:
#         cart = Cart.objects.filter(user=user)
#         amount = 0
#         for p in cart:
#             value = p.quantity * p.product.discounted_price
#             amount += value
#         totalamount = amount + 40  # Add shipping or handling fee
#         totalitem = len(cart)
#     else:
#         # If the user is not authenticated, set empty values
#         cart = []
#         totalamount = 0
#         totalitem = 0

#     return render(request, 'app/addtocart.html', {
#         'cart': cart,
#         'totalamount': totalamount,
#         'totalitem': totalitem
#     })
    
    
    
# @login_required
# def checkout(request):
#     user = request.user
#     cart_items = Cart.objects.filter(user=user)

#     totalamount = sum(item.product.discounted_price * item.quantity for item in cart_items) + 40  # Rs. 40 Shipping

#     addresses = Customer.objects.filter(user=user)

#     if request.method == 'POST':
#         selected_address_id = request.POST.get('custid')

#         if not selected_address_id:
#             messages.error(request, "Please select a shipping address.")
#             return redirect('checkout')

#         selected_address = Customer.objects.get(id=selected_address_id)

#         # Create Order (Assuming single-product order for simplicity)
#         order = OrderPlaced.objects.create(
#             user=user,
#             customer=selected_address,
#             product=cart_items[0].product,
#             quantity=cart_items[0].quantity,
#             status='Pending',
#             shipping_address=selected_address
#         )

#         # Create a Payment record with Pending status
#         payment = Payment.objects.create(
#             order=order,
#             amount_paid=totalamount - 40,  # Excluding shipping from payment amount
#             payment_status=Payment.PENDING
#         )
#         order.payment = payment
#         order.save()

#         # Redirect to Payment Selection Page
#         return redirect('payment_selection', order_id=order.id)

#     return render(request, 'app/checkout.html', {
#         'cart_items': cart_items,
#         'totalamount': totalamount,
#         'add': addresses,
#     })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import OrderPlaced, Payment, PaymentReceipt, Cart, Customer

@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    totalamount = sum(item.product.discounted_price * item.quantity for item in cart_items) + 40  # Rs. 40 Shipping
    addresses = Customer.objects.filter(user=user)

    if request.method == 'POST':
        selected_address_id = request.POST.get('custid')
        if not selected_address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect('checkout')
        selected_address = Customer.objects.get(id=selected_address_id)

        # Create a single payment first
        payment = Payment.objects.create(
            amount=totalamount,
            status=Payment.PENDING,
            method=Payment.PAYMENT_METHOD_COD  # will be updated in selection
        )

        # Create orders for each cart item and link to the same payment
        for item in cart_items:
            OrderPlaced.objects.create(
                user=user,
                customer=selected_address,
                product=item.product,
                quantity=item.quantity,
                status='Pending',
                shipping_address=selected_address,
                payment=payment
            )

        # Clear the cart after placing order
        cart_items.delete()

        return redirect('payment_selection', payment_id=payment.id)


    return render(request, 'app/checkout.html', {
        'cart_items': cart_items,
        'totalamount': totalamount,
        'add': addresses,
    })


# @login_required
# def checkout(request):
#     user = request.user
#     cart_items = Cart.objects.filter(user=user)
#     totalamount = sum(item.product.discounted_price * item.quantity for item in cart_items) + 40  # Rs. 40 Shipping
#     addresses = Customer.objects.filter(user=user)

#     if request.method == 'POST':
#         selected_address_id = request.POST.get('custid')
#         if not selected_address_id:
#             messages.error(request, "Please select a shipping address.")
#             return redirect('checkout')
#         selected_address = Customer.objects.get(id=selected_address_id)
        
#         order = OrderPlaced.objects.create(
#             user=user,
#             customer=selected_address,
#             product=cart_items[0].product,
#             quantity=cart_items[0].quantity,
#             status='Pending',
#             shipping_address=selected_address
#         )
        
#         payment = Payment.objects.create(
#             order=order,
#             amount=totalamount - 40,
#             status=Payment.PENDING,  # Default pending
#             method=Payment.PAYMENT_METHOD_COD  # Default to COD, updated later if needed
#         )

#         return redirect('payment_selection', order_id=order.id)

#     return render(request, 'app/checkout.html', {
#         'cart_items': cart_items,
#         'totalamount': totalamount,
#         'add': addresses,
#     })

@login_required
def payment_selection(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    orders = OrderPlaced.objects.filter(payment=payment)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        payment.method = payment_method
        payment.save()

        if payment_method == "online":
            return redirect('secure_payment', payment_id=payment.id)
        else:
            return redirect('payment_receipt', payment_id=payment.id)

    return render(request, 'app/payment_selection.html', {
        'payment': payment,
        'orders': orders
    })

from django.utils.timezone import now
@login_required
def secure_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    orders = OrderPlaced.objects.filter(payment=payment)

    if not orders.exists():
        messages.error(request, "No orders found for this payment.")
        return redirect('cart')

    if request.method == 'POST':
        card_number = request.POST.get('cardNumber', '').strip()
        expiry_month = request.POST.get('expityMonth', '').strip()
        expiry_year = request.POST.get('expityYear', '').strip()
        cv_code = request.POST.get('cvCode', '').strip()

        # --- Validation ---
        if not (card_number.isdigit() and len(card_number) == 16):
            messages.error(request, "Card number must be exactly 16 digits.")
            return redirect('secure_payment', payment_id=payment.id)

        if not (cv_code.isdigit() and len(cv_code) == 3):
            messages.error(request, "CVV must be exactly 3 digits.")
            return redirect('secure_payment', payment_id=payment.id)

        try:
            expiry_month = int(expiry_month)
            expiry_year = int(expiry_year)
        except ValueError:
            messages.error(request, "Invalid expiry date format.")
            return redirect('secure_payment', payment_id=payment.id)

        current_year = datetime.now().year % 100
        current_month = datetime.now().month

        if expiry_year < current_year or (expiry_year == current_year and expiry_month < current_month):
            messages.error(request, "Card expiry date is invalid or in the past.")
            return redirect('secure_payment', payment_id=payment.id)

        # --- Save payment details ---
        payment.card_number = card_number
        payment.expiry_month = expiry_month
        payment.expiry_year = expiry_year
        payment.cvv = cv_code
        payment.status = Payment.SUCCESS
        payment.date = now()
        payment.save()

        # --- Update all linked orders ---
        for order in orders:
            order.status = 'Confirmed'
            order.save()

        messages.success(request, "Payment successful!")
        return redirect('payment_receipt', payment_id=payment.id)

    # Total = sum of all order prices + delivery (if any)
    total_price = sum(order.total_cost for order in orders) + 40


    return render(request, 'app/payment_process.html', {
        'payment': payment,
        'orders': orders,
        'total': total_price
    })



@login_required
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    orders = OrderPlaced.objects.filter(payment=payment)

    if not orders.exists():
        messages.error(request, "No orders found for this payment.")
        return redirect('cart')

    subtotal = sum(order.product.discounted_price * order.quantity for order in orders)
    shipping = 40
    total = subtotal + shipping

    return render(request, 'app/payment_receipt.html', {
        'payment': payment,
        'orders': orders,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })



def download_receipt(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    orders = OrderPlaced.objects.filter(payment=payment)
    
    subtotal = sum(order.total_cost for order in orders)
    shipping = 50 if subtotal < 1000 else 0
    total = subtotal + shipping

    template_path = 'app/receipt_pdf.html'
    context = {
        'payment': payment,
        'orders': orders,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors generating the receipt <pre>' + html + '</pre>')
    return response    


@login_required
def order_confirmation(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    orders = OrderPlaced.objects.filter(payment=payment)

    subtotal = sum(order.product.discounted_price * order.quantity for order in orders)
    shipping = 40
    total = subtotal + shipping

    return render(request, 'app/order_confirmation.html', {
        'payment': payment,
        'orders': orders,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })



# @login_required
# def payment_receipt(request, order_id):
#     order = get_object_or_404(OrderPlaced, id=order_id)
#     payment = order.payment
#     orders = OrderPlaced.objects.filter(payment=payment)
#     first_order = orders.first()
#     return render(request, 'app/payment_receipt.html', {
#         'orders': orders,
#         'payment': payment,
#         'first_order': first_order
#     })



# @login_required
# def order_confirmation(request, order_id):
#     order = get_object_or_404(OrderPlaced, id=order_id)
#     payment = order.payment
#     orders = OrderPlaced.objects.filter(payment=payment)
#     return render(request, 'app/order_confirmation.html', {'orders': orders, 'payment': payment})




@login_required
def order_history(request):
    orders = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'app/order_history.html', {'orders': orders})







from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import ContactForm
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send the email to the admin (your email address) with the user's info
            send_mail(
                subject,
                f"Message from {name} ({email}):\n\n{message}",
                email,  # User's email will appear in the 'From' field
                [settings.CONTACT_EMAIL],  # Your email will appear in the 'To' field
                fail_silently=False,
            )

            # Add a success message
            messages.success(request, 'Your message has been sent successfully!')

            # Render the same form page with success message
            return render(request, 'app/contact.html', {'form': form})

    else:
        form = ContactForm()

    return render(request, 'app/contact.html', {'form': form})






# def success_view(request):
#     return render(request, 'app/success.html')



# used some AJAX and js check myscript.js 
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        
        # Get all cart items for the user and product
        carts = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if carts.exists():
            # If there are multiple items, choose the first one (or you could sum quantities)
            c = carts.first()
            c.quantity += 1
            c.save()
        else:
            # Optionally handle the case where the cart entry doesn't exist
            # You might want to create a new Cart object here
            return JsonResponse({'error': 'Cart item not found.'}, status=404)
        
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount += value
        totalamount = amount + 40  # Add any fixed charges

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        
        # Get all cart items for the user and product
        carts = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if carts.exists():
            c = carts.first()  # Choose the first item if there are multiple
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            else:
                # Optionally, you could delete the cart item if quantity is 1
                c.delete()
        else:
            return JsonResponse({'error': 'Cart item not found.'}, status=404)

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount += value
        totalamount = amount + 40  # Add any fixed charges

        data = {
            'quantity': c.quantity if c.quantity > 0 else 0,  # Ensure quantity is not negative
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)    
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        
        # Use filter to get all cart items for the user and product
        carts = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if carts.exists():
            # Optionally, you can remove all items or just one; here we remove the first found
            carts.first().delete()  # Deletes the first matching cart entry
        else:
            return JsonResponse({'error': 'Cart item not found.'}, status=404)

        # Calculate the total amount after removal
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount += value
            
        totalamount = amount + 40  # Add fixed charges

        data = {
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
        
@login_required
def show_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items})
        
@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return JsonResponse({'message': 'Wishlist Added Successfully'})

@login_required
def minus_wishlist(request):    
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user, product=product).delete()  # ✅ FIXED LINE
        data = {
            'message': 'Wishlist Removed Successfully'
        }    
        return JsonResponse(data)

@login_required
def search(request):
    query = request.GET.get('search', '')
    totalitem = 0
    wishitem = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    
    # Correct the field lookup to use double underscores
    product = Product.objects.filter(Q(title__icontains=query))
    
    return render(request, "app/search.html", locals())


import os
import pickle
import django
import torch
from django.conf import settings
from django.shortcuts import render
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import models, transforms
from PIL import Image

# Setup Django (if needed)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import Product  # after django.setup()

# Load pre-trained ResNet model (excluding the classification layer)
model = models.resnet18(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

#  Updated to accept both file paths and image objects
def get_embedding(image_input):
    if isinstance(image_input, str):  # If it's a file path
        image = Image.open(image_input).convert('RGB')
    else:  # If it's a file-like object (like uploaded file)
        image = image_input.convert('RGB')

    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = model(image)
    return embedding.squeeze().numpy()


#  Generate product embeddings and save to a file
def generate_product_embeddings():
    embeddings = {}
    for product in Product.objects.all():
        if product.product_image and os.path.exists(product.product_image.path):
            embeddings[product.id] = get_embedding(product.product_image.path)

    file_path = os.path.join(settings.BASE_DIR, 'product_embeddings.pkl')
    with open(file_path, 'wb') as f:
        pickle.dump(embeddings, f)
        
def image_search(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        img = Image.open(uploaded_image)
        uploaded_embedding = get_embedding(img).reshape(1, -1)

        file_path = os.path.join(settings.BASE_DIR, 'product_embeddings.pkl')

        if not os.path.exists(file_path):
            return render(request, 'app/image_upload.html', {
                'error': 'Embeddings file not found. Please generate embeddings first.'
            })

        with open(file_path, 'rb') as f:
            product_embeddings = pickle.load(f)

        best_match = None
        best_similarity = 0.0

        for pid, emb in product_embeddings.items():
            sim = cosine_similarity(uploaded_embedding, emb.reshape(1, -1))[0][0]
            if sim > best_similarity:
                best_similarity = sim
                best_match = pid

        if best_match and best_similarity > 0.5:  # Set a threshold to avoid bad matches
            product = Product.objects.get(id=best_match)
            return render(request, 'app/image_results.html', {
                'product': product,
                'similarity': f'{best_similarity:.2f}'
            })
        else:
            return render(request, 'app/image_results.html', {
                'message': 'No matching product found.'
            })

    return render(request, 'app/image_upload.html')
