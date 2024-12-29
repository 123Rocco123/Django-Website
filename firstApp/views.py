import os
import time
import requests

import numpy as np
import pandas as pd
import yfinance as yf

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

# Function used to order the values in the dataframe by the datetime
def returnedOrderedDate(dataframe, dateColumn="date"):
    # Converts the date column to a datetime object
    dataframe[dateColumn] = pd.to_datetime(dataframe[dateColumn])
    # Orders the dataframe by the date column
    dataframe = dataframe.sort_values(by=dateColumn)

    # Contains the array used for the datetime column
        # In string format
    dateColumnArr = []
    # Iterates through the date column to convert and add the string date to the dateColunn
    for date in dataframe[dateColumn]:
        dateColumnArr.append(f"{date.month}/{date.day}/{date.year}")

    # Converts the date column back to a string
    dataframe[dateColumn] = dateColumnArr

    return dataframe

# Function used to remove dates from the prediction dataframe
    # These are values which are less than the most recent date and not in the date of the stock values
def removeIncorrectDates(stockName, dataFrame):
    # Contains the stock values
    stockValues = pd.read_csv(f"{os.getcwd()}/database/StockValues/{stockName}/{stockName}.csv")

    # Contains the most recent date in datetime format
        # Used so that we can check if we have to remove the date or we can keep it as a future prediciton
    mostRecentDate = pd.to_datetime(stockValues["date"].tail(1).values[0])
    # Contains the dates which are not in the stock values
        # Used so that we can remove them from the dates of the preditions
    datesToRemove = [x for x in dataFrame["date"] if (pd.to_datetime(x) < mostRecentDate) and (x not in stockValues["date"].tolist())]

    # Removes the dates from the predictions
    dataFrame = dataFrame[~dataFrame["date"].isin(datesToRemove)]
    # Returns the predictions
    return dataFrame

# Function used to return the formal name of the stock
def returnFormalName(stockName):
    # Contains the formal stock name, ticker, of the function
    formalName = pd.read_csv(f"{os.getcwd()}/database/stockInformation.csv")
    formalName = formalName[formalName["Informal Stock Name"] == stockName]["Formal Stock Name"].values[0]

    return formalName

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

# Function used to return the buttons 
def returnPredictionModels(request):
    stock_name = request.GET.get('stock_name')

    if not stock_name:
        return JsonResponse({'error': 'Stock name is required'}, status=400)
    
    filePath = f"{os.getcwd()}/database/Predictions/{stock_name}/"
    
    if not os.path.exists(filePath):
        return JsonResponse({'error': f'Stock data for {stock_name} not found'}, status=404)

    try:
        return JsonResponse({'predictions': [x.replace(".csv", "") for x in os.listdir(f"{filePath}/linearRegression/")]}, status=200)
    except Exception as e:
        return JsonResponse({'error': 'Failed to read articles', 'details': str(e)}, status=500)

# Function used to return the news articles for the specific user selected stock
def getStockArticles(request):
    stock_name = request.GET.get('stock_name')

    if not stock_name:
        return JsonResponse({'error': 'Stock name is required'}, status=400)
    
    # Path to the articles file
    file_path = os.path.join(os.getcwd(), "database", "NaturalLanguage", "Newspapers", stock_name, "articles.csv")
    
    if not os.path.exists(file_path):
        return JsonResponse({'error': f'Stock data for {stock_name} not found'}, status=404)

    try:
        # Reads the articles file and returns the 25 most recent articles
        articles_df = returnedOrderedDate(pd.read_csv(file_path), "Date Posted").tail(25)
        # Returns the inverted dictionary so as to display the most recent articles first
        articles = articles_df.to_dict(orient='records')[::-1]

        return JsonResponse({'articles': articles}, status=200)
    except Exception as e:
        return JsonResponse({'error': 'Failed to read articles', 'details': str(e)}, status=500)

# Function used to return the daily stock values for the clicked stock
def getStockValues(request):
    stock_name = request.GET.get('stock_name')

    if not stock_name:
        return JsonResponse({'error': 'Stock name is required'}, status=400)
    
    try:
        file_path = os.path.join(os.getcwd(), "database", "StockValues", stock_name, f"{stock_name}.csv")
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'Stock data for {stock_name} not found'}, status=404)

        file = pd.read_csv(file_path)
        if file.empty or "date" not in file or "Close" not in file:
            return JsonResponse({'error': f'Invalid data in {file_path}'}, status=400)

        # Prepare the data for the response
        stock_values = file.to_dict(orient="records")
        for entry in stock_values:
            # If condition used to make sure that the stock value is readable when its worth much less
                # And becomes more readable when its worth more
            entry["open"]     = round(entry["Open"], 4) if entry["Open"] < 1 else round(entry["Open"], 2)
            entry["high"]     = round(entry["High"], 4)
            entry["low"]      = round(entry["Low"], 4)
            entry["closing"]  = round(entry["Close"], 4)
            entry["volume"]   = entry["Volume"]

        return JsonResponse({"stock_values": stock_values[::-1]}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Function used to return the recommendations made by instiutions about the selected stock
def returnRecommendations(request):
    stock_name = request.GET.get('stock_name')

    # Contains the dataframe for the recommendations
    recommendationValues = pd.read_csv(f"{os.getcwd()}/database/Company/{stock_name}/recommendations/analystRecommendations.csv")

    if recommendationValues.empty or "date" not in recommendationValues:
        return JsonResponse({'error': f'Invalid data in {os.path.abspath(recommendationValues)}'}, status=400)

    # Prepare the data for the response
    stock_values = recommendationValues.to_dict(orient="records")

    for entry in stock_values:
        entry["date"]        = entry["date"]
        entry["strong_buy"]  = entry["strongBuy"]
        entry["buy"]         = entry["buy"]
        entry["hold"]        = entry["hold"]
        entry["sell"]        = entry["sell"]
        entry["strong_sell"] = entry["strongSell"]
        entry["total"]       = entry["number of analysts"]

    return JsonResponse({"recommendations": stock_values[::-1]}, status=200)

# Function used to return the price targets for the selected stock
def returnPriceTargets(request):
    stock_name = request.GET.get('stock_name')

    # Contains the dataframe for the recommendations
    recommendationValues = pd.read_csv(f"{os.getcwd()}/database/Company/{stock_name}/recommendations/analystPriceTargets.csv")

    if recommendationValues.empty or "date" not in recommendationValues:
        return JsonResponse({'error': f'Invalid data in {os.path.abspath(recommendationValues)}'}, status=400)

    # Prepare the data for the response
    stock_values = recommendationValues.to_dict(orient="records")

    for entry in stock_values:
        entry["date"]    = entry["date"]
        entry["low"]     = entry["low"]
        entry["high"]    = entry["high"]
        entry["mean"]    = round(entry["mean"], 2)
        entry["median"]  = entry["median"]
        entry["current"] = entry["current"]
        entry["more"]    = True if entry["mean"] > entry["current"] else False

    return JsonResponse({"priceTargets": stock_values[::-1]}, status=200)

# Function used to return the gathered ratings for the selected stock
def returnStockRatings(request):
    stock_name = request.GET.get('stock_name')

    # Contains the dataframe for the recommendations
    recommendationValues = pd.read_csv(f"{os.getcwd()}/database/Company/{stock_name}/recommendations/ratings.csv")

    recommendationValues = recommendationValues.fillna("N/A")

    if recommendationValues.empty or "Reported Date" not in recommendationValues:
        return JsonResponse({'error': f'Invalid data in {os.path.abspath(recommendationValues)}'}, status=400)

    # Prepare the data for the response
    stock_values = recommendationValues.to_dict(orient="records")

    for entry in stock_values:
        entry["date"]      = entry["Reported Date"]
        entry["Firm"]      = entry["Firm"]
        entry["FromGrade"] = entry["FromGrade"]
        entry["ToGrade"]   = entry["ToGrade"]
        entry["Outlook"]   = entry["Outlook"]

    return JsonResponse({"ratings": stock_values[::-1]}, status=200)

# Function used to return the closing and afterhours prices of the stock
def returnStockClosingPrices(request):
    stockName = request.GET.get('stock_name')

    # Contains the formal stock name, ticker, of the function
    formalName = returnFormalName(stockName)
    # Contains the yahoo finance information about the stock
    stockInformation = yf.Ticker(formalName).info

    # Variable contains the symbol of the currency of the stock
    currency = "$" if stockInformation["currency"] == "USD" else "€"

    # Contains the afterhours values of the stock
        # We get the most recent afterhours values
    afterHoursFiles = os.listdir(f"{os.getcwd()}/database/StockValues/{stockName}/afterHours/")
    afterHours      = [pd.to_datetime(x[x.index("_") + 1 : ].replace("_", "/")) for x in afterHoursFiles]
    afterHours      = sorted(afterHours)[-1]
    
    # Convert the afterHours variable to a string
    afterHours      = f"{afterHours.month}_{afterHours.day}_{afterHours.year}"
    afterHoursFiles = [x for x in afterHoursFiles if afterHours in x][0]

    # Contains the afterhours values of the stock
    afterHours = pd.read_csv((f"{os.getcwd()}/database/StockValues/{stockName}/afterHours/{afterHoursFiles}"))
    afterHours = afterHours["Close"].values.tolist()[-1]

    closingValues = pd.read_csv(f"{os.getcwd()}/database/StockValues/{stockName}/{stockName}.csv")
    closingValues = closingValues["Close"].values.tolist()[-1]

    return JsonResponse({"closing": round(closingValues, 2), "afterHours": round(afterHours, 2), "currency" : currency}, status=200)

def get_model_prediction(request):
    stock_name = request.GET.get('stock_name')
    model_name = request.GET.get('model_name')

    if not stock_name or not model_name:
        return JsonResponse({'error': 'Stock name and model name are required'}, status=400)
    
    try:
        file_path = os.path.join(f"{os.getcwd()}/database/Predictions/{stock_name}/linearRegression", f"{model_name}.csv")
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'Model data for {model_name} not found'}, status=404)

        file = pd.read_csv(file_path)

        if file.empty or "date" not in file or "daily prediction" not in file:
            return JsonResponse({'error': 'Invalid data in model file'}, status=400)
        
        else:
            # Organizes the dataframe by the date
            file = returnedOrderedDate(file)
            file = removeIncorrectDates(stock_name, file)

            # Ensure date and prediction arrays match
            dates = pd.to_datetime(file["date"])
            predictions = file["daily prediction"].tolist()

            if len(dates) < len(predictions):
                # Calculate the interval between dates
                date_diff = dates.diff().mean()  # Average difference
                if pd.isna(date_diff):  # Handle edge case for single date
                    date_diff = pd.Timedelta(days=1)
                
                # Generate additional dates
                extra_dates = [dates.iloc[-1] + i * date_diff for i in range(1, len(predictions) - len(dates) + 1)]
                # Extend the dates list
                dates = dates.tolist() + extra_dates

            # Convert extended dates back to strings for JSON response
            extended_dates = [date.strftime(f'{date.month}/{date.day}/{date.year}') for date in dates]

            return JsonResponse({
                "data": {
                    "x": extended_dates,
                    "y": predictions
                }
            }, status=200)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

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
