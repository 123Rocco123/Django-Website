import os

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

def aboutMe(request):
    # Read the content of the .txt file
    with open(f"{os.getcwd()}/firstApp/texts/letterToReader.txt", 'r', encoding='utf-8') as file:
        file_content = file.read()
    
    #file_content = os.getcwd()

    return render(request, 'firstApp/about.html', {'letter': file_content})

# Different subpage to the first app directory
    # I.e. Subdirectory
def projectIdea(request):
    return HttpResponse("<h1>Project Idea</h1>")
