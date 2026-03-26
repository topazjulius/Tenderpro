from django.shortcuts import redirect


def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper