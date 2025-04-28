from django.http import HttpResponseForbidden
from .models import Customer

def is_customer(user):
    return Customer.objects.filter(user=user).exists()

def user_is_customer(function):
    def wrap(request, *args, **kwargs):
        if not is_customer(request.user):
            return HttpResponseForbidden("You must be a customer to access this page.")
        return function(request, *args, **kwargs)
    return wrap
