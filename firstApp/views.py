import os
import time
import requests

import pandas as pd

from datetime import date

# Used for reading websites
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from plotly.offline import plot
from plotly.graph_objs import Scatter

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# ----------------------------------------------------------------------------------------------------------------------------------------
#                                                           Auxiliary Functions
# ----------------------------------------------------------------------------------------------------------------------------------------

# Function used to gather the most recent stock values for the specified stock
def returnIsProfitable(stock):
    # Variable used to contain the stock information of the passed in company
    stockInformation = pd.read_csv(f"{os.getcwd()}/database/StockValues/{stock}/{stock}.csv").tail(2)

    # Returns True if today the stock increased in value
        # False if the opposite is true
    return stockInformation["Close"].tolist()[0] < stockInformation["Close"].tolist()[1]

# Function returns the most recent stock price
def returnPrice(stock):
    # Variable used to contain the stock information of the passed in company
    stockInformation = pd.read_csv(f"{os.getcwd()}/database/StockValues/{stock}/{stock}.csv").tail(1)

    # Returns True if today the stock increased in value
        # False if the opposite is true
    return round(float(stockInformation["Close"].values.tolist()[0]), 4)

def returnCurrency(stock):
    currencies = {"$" : ["TSMC", "Visa", "Nvidia", "ARM", "AMD"],
                  "€" : ["Unicredit"]}

    for values in currencies:
        if stock in currencies[values]:
            return values

# LOGO FUNCTIONS

# Function used to set driver to headless mode
    # While also making it so that we run it with a virtual window
def virtualWindow():
    options = Options()
    # Simulate a real window
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    # Set the window size
    options.add_argument("--window-size=1920x1080")
    # Used to attempt to disable headless mode website detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Disabling GPU can help with headless mode stability
    options.add_argument("--disable-gpu")
    # Used to run the chrome driver without opening the browser
    options.add_argument('--headless=new')

    return options

# Function used to reject the cookies searching something on Google
def rejectGoogleCookies(driver):
    rejectAll = [x for x in driver.find_elements(By.TAG_NAME, "button") if x.text == "Reject all"][0]
    rejectAll.click()

# Function used to find and download the company's logo
    # Used if we don't have one
def findCompanyLogo(stockName):
    # Contains the options for the driver
    driver = webdriver.Chrome()#options = virtualWindow())

    driver.get(f"https://www.google.com/search?q={stockName}+wikipedia+logo")
    # Reject Google Cookies
    rejectGoogleCookies(driver)
    # Find elements with alt attribute containing '- Wikipedia'
    driver.find_element(By.XPATH, "//*[@alt and contains(@alt, '- Wikipedia')]").click()

    # Load Image
    time.sleep(1)

    try:
        firstImage = driver.find_element(By.CSS_SELECTOR, f"[alt*='File:{stockName} Logo.svg - Wikipedia']").get_attribute("src")

        try:
            img_response = requests.get(firstImage)
        except:
            firstImage = driver.find_elements(By.CSS_SELECTOR, f"[alt*='File:{stockName} Logo.svg - Wikipedia']")[1].get_attribute("src")
    except:
        try:
            # Find all img elements with "https://upload.wikimedia.org/wikipedia/" in the src attribute
            firstImage = driver.find_element("xpath", "//img[contains(@src, 'https://upload.wikimedia.org/wikipedia/')]").get_attribute("src")
        except:
            firstImage = driver.find_elements("xpath", "//img[contains(@alt, '- Wikipedia')]")[0].get_attribute("src")

    img_response = requests.get(firstImage)

    if img_response.status_code == 200:
        with open(f"{os.getcwd()}/firstApp/static/firstApp/images/{stockName}.png", 'wb') as file:
            file.write(img_response.content)

    driver.close()

# Function used to return the stock specific logo
    # It will get one off of google if we don't have it already
def checkForLogo(stockName):
    if os.path.exists(f"{os.getcwd()}/firstApp/static/firstApp/images/{stockName}.png"):
        return f"{stockName}.png"
    else:
        try:
            findCompanyLogo(stockName)
        except:
            return None

# ----------------------------------------------------------------------------------------------------------------------------------------
#                                                              Views Functions
# ----------------------------------------------------------------------------------------------------------------------------------------

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

    with open(f"{os.getcwd()}/firstApp/texts/footer.txt", 'r', encoding='utf-8') as file:
        footer = file.read()

    return render(request, 'firstApp/index.html', {'timeline': timeline,
                                                   "ftbi" : featurestbImplemented,
                                                   "importantMessages" : importantMessages,
                                                   "footer" : footer})

def get_stock_graph(request):
    stock_name = request.GET.get('stock_name')  # Get the stock name from the GET parameter
    if not stock_name:
        return JsonResponse({'error': 'Stock name is required'}, status=400)
    
    try:
        file_path = os.path.join(os.getcwd(), "database", "StockValues", stock_name, f"{stock_name}.csv")
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'Stock data for {stock_name} not found'}, status=404)

        file = pd.read_csv(file_path)  # Load the last 20 records
        if file.empty or "date" not in file or "Close" not in file:
            return JsonResponse({'error': f'Invalid data in {file_path}'}, status=400)

        # Prepare the data for Plotly
        x_data = file["date"].tolist()
        y_data = file["Close"].tolist()

        # Return the data needed for Plotly.newPlot
        graph_data = {
            "data": [
                {
                    "x": x_data,
                    "y": y_data,
                    "type": "scatter",
                    "mode": "lines",
                    "name": stock_name,
                    "opacity": 0.8,
                    "line": {"color": "black"}
                }
            ],
            "layout" : {
            "title": f"{stock_name} Stock Prices",
            "xaxis": {
                "title": {
                    "text": "Date",
                    "standoff": 20  # Space between title and axis ticks (better way)
                },
                "autorange": True,  # Auto-adjust the x-axis range
                "ticks": "outside",  # Ensure ticks are outside the plot for more spacing
                "showgrid": True,  # Optional: Show grid lines for better clarity
            },
            "yaxis": {
                "title": "Close Price",
                "autorange": True,  # Auto-adjust the y-axis range
                "range": [min(y_data) * 0.9, max(y_data) * 1.1],  # Set a zoomed-out y-axis range
            },
            "autosize": True,
            "margin": {"l": 50, "r": 50, "t": 50, "b": 100},  # Increase bottom margin for space
        }}
        return JsonResponse(graph_data, status=200)
    
    except Exception as e:
        print(f"Error fetching stock graph: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

def portfolioHome(request):
    # Variable used to contain the file names of the tracked stocks
        # Used so that we can display the options (initially only)
    allowedStocks = [{"name" : stock, "currency" : returnCurrency(stock), "price" : returnPrice(stock), "logo" : checkForLogo(stock), "is_profitable" : returnIsProfitable(stock)}
                     for stock in os.listdir(f"{os.getcwd()}/database/StockValues/")]

    return render(request, 'firstApp/portfolioHome.html', context={"stocks" : allowedStocks})

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
