from datetime import date

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# Function used to initialize the webpage
    # Sending us to the index.html page
def index(request):
    return render(request, 'firstApp/index.html')

def register(request):
    return render(request, 'firstApp/createAccount.html')

def login(request):
    return render(request, 'firstApp/login.html')

def pricing(request):
    timer = date(month=1, day=1, year=2027)
    timer = (timer - date.today()).days

    context = {
        "timer" : timer
    }

    return render(request, 'firstApp/pricing.html', context)

# Different subpage to the first app directory
    # I.e. Subdirectory
def projectIdea(request):
    return HttpResponse("<h1>Project Idea</h1>")
