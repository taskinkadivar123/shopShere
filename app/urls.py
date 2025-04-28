from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MyPasswordResetForm,MyPasswordChangeForm,MySetPasswordForm
from django.urls import reverse_lazy



urlpatterns = [
    path('', views.home, name='home'),  
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),  
    # path('contact/', views.contact, name='contact'), 
    path('contact/', views.contact_view, name='contact'),
    path('image-search/', views.image_search, name='image_search'),
    path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
    path('category-title/<val>', views.CategoryTitle.as_view(), name='category-title'),  # Ensure this matches the view name exactly
    path('product-detail/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.addresss, name='address'),
    path('updateAddress/<int:pk>/', views.updateAddress.as_view(), name='updateAddress'),  # Ensure this line is correct
    
    
    path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    path('cart/',views.show_cart,name='showcart'),
    # path('checkout/', views.checkout.as_view(), name='checkout'), 
    path('pluscart/', views.plus_cart, name='plus_cart'),
    path('minuscart/', views.minus_cart, name='minus_cart'),
    path('removecart/', views.remove_cart, name='remove_cart'),
    path('pluswishlist/', views.plus_wishlist, name='plus_wishlist'),
    path('minuswishlist/', views.minus_wishlist, name='minus_wishlist'),
    path('wishlist/', views.show_wishlist, name='wishlist'),
    path('search/',views.search,name='search'),
    # path('orders/',views.orders,name='orders'),
    
    
    # path('checkout/', views.checkout, name='checkout'),
    # path('customer-address', views.customer_address_view,name='customer-address'),
    # path('payment-success', views.payment_success_view,name='payment-success'),
    # path('payment-process/', views.payment_process_view, name='payment_process'),
    # path('order-history/', views.order_history, name='order_history'),
    # path('payment-success/', views.payment_success_view, name='payment_success'),
    
    
    # path('checkout/', views.checkout, name='checkout'),
    # path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    # path('payment_selection/<int:order_id>/', views.payment_selection, name='payment_selection'),

    # path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),


    path('checkout/', views.checkout, name='checkout'),
    path('payment-selection/<int:payment_id>/', views.payment_selection, name='payment_selection'),
    path('secure-payment/<int:payment_id>/', views.secure_payment, name='secure_payment'),
    path('payment-receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    path('order-confirmation/<int:payment_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('download-receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    # path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
   
    # path('download_invoice/<int:orderID>/<int:productID>/', views.download_invoice_view, name='download_invoice'),

    path('admin_login/', views.login_view, name='admin_login'),
    path('admin_register/', views.register_view, name='admin_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/users/', views.dashboard_users, name='dashboard_users'),
    path('dashboard/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    # path('dashboard/users/', views.user_management, name='user_management'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/carts/', views.dashboard_carts, name='dashboard_carts'),
    path('delete-cart-item/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('dashboard/wishlists/', views.dashboard_wishlists, name='dashboard_wishlists'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/edit/<int:pk>/', views.edit_order, name='edit_order'),
    path('dashboard/orders/delete/<int:pk>/', views.delete_order, name='delete_order'),
    path('dashboard/payment/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('dashboard/payments/', views.dashboard_payments, name='dashboard_payments'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/add/', views.add_product, name='add_product'),
    path('dashboard/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('dashboard/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('dashboard/data/', views.dashboard_data, name='dashboard_data'),

    
    #login
    path('customerregistration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),  # Corrected view class
    path('accounts/login/',auth_view.LoginView.as_view(template_name='app/login.html',authentication_form=LoginForm),name='login'),
    path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html', 
        form_class=MyPasswordChangeForm, success_url='/passwordchangedone'), name='passwordchange'),
    path('passwordchangedone/', auth_view.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), 
        name='passwordchangedone'),
    path('logout/', auth_view.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
    template_name='app/password_reset.html',
    email_template_name='app/password_reset_email.html',
    subject_template_name='app/password_reset_subject.txt',
    success_url=reverse_lazy('password_reset_done'),  # Updated to use reverse_lazy
    form_class=MyPasswordResetForm,
), name='password_reset'),

    # Password Reset Done (Confirmation page after email is sent)
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='app/password_reset_done.html'
    ), name='password_reset_done'),

    # Password Reset Confirm (Enter the new password)
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='app/password_reset_confirm.html',
        form_class=MySetPasswordForm  # Custom form (if needed) to reset the password
    ), name='password_reset_confirm'),

    # Password Reset Complete (Confirmation page after password is reset)
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='app/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
    template_name='app/password_reset.html', 
    form_class=MyPasswordResetForm), name='password_reset'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='app/password_reset_confirm.html', 
    form_class=MySetPasswordForm), name='password_reset_confirm'),
    
    # path('password-reset/',auth_view.PasswordResetView.as_view(template_name='app/password_reset_done.html',form_class=MyPasswordResetForm),
    #     name='password_reset'),
    # path('password-reset/done/',auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'),
    #     name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html',
    #     form_class=MySetPasswordForm),name='password_reset_confirm'),
    # path('password-reset-complete/',auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'),
    #     name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header ="Taskin Kadivar"
admin.site.site_title ="Taskin Kadivar"
admin.site.site_index_title ="Welcome to Taskin Kadivar's Shop"