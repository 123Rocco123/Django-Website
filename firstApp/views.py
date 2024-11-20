import os

from datetime import date

from plotly.offline import plot
from plotly.graph_objs import Scatter

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# Function used to initialize the webpage
    # Sending us to the index.html page
def index(request):
    # Read the content of the .txt file
    with open(f"{os.getcwd()}/firstApp/texts/timeline.txt", 'r', encoding='utf-8') as file:
        timeline = file.read()

    with open(f"{os.getcwd()}/firstApp/texts/FtbI.txt", 'r', encoding='utf-8') as file:
        featurestbImplemented = file.read()

    with open(f"{os.getcwd()}/firstApp/texts/importantmessages.txt", 'r', encoding='utf-8') as file:
        importantMessages = file.read()

    return render(request, 'firstApp/index.html', {'timeline': timeline, "ftbi" : featurestbImplemented, "importantMessages" : importantMessages})

def portfolioHome(request):
    x_data = [0,1,2,3]
    y_data = [x**2 for x in x_data]
    plot_div = plot([Scatter(x=x_data, y=y_data,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='green')],
               output_type='div')

    return render(request, 'firstApp/portfolioHome.html', context={'plot_div': plot_div})

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
