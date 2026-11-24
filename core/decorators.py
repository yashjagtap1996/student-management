from django.contrib import messages
from django.shortcuts import redirect

def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue.")
            return redirect('signin')

        if not request.user.is_superuser:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('home')  # or home page

        return view_func(request, *args, **kwargs)
    return wrapper