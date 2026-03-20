from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def register_vendor(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(username=username, password=password)

        return redirect('login')

    return render(request, 'accounts/register.html')


def login_vendor(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/tenders/')

    return render(request, 'accounts/login.html')


def logout_vendor(request):
    logout(request)
    return redirect('/')