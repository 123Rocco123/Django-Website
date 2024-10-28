from django.shortcuts import render, redirect
from .forms import RegisterForm

from django.contrib import messages
from django.contrib.auth import logout

# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)

        if form.is_valid():
            form.save()

        return redirect("/")
    else:
        form = RegisterForm()

    return render(response, "register/createAccount.html", {"form" : form})

def logout_user(response):
    logout(response)
    messages.success(response, ("You have successfully been logged out"))

    return redirect("/")