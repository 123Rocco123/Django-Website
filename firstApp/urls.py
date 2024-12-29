# Used to import the paths function from Django
from django.urls import path, include
# Used to import the views file from the same directory
from . import views

urlpatterns = [
    # An empty path, "", signifies that we want it to me the homepage
        # The view.index is what handles the logic
        # The "name = ..." parameter is used to set the name of the page
    path("", views.index, name = "index"),
    # Contains the view link to the pricing page
    path("pricing/", views.pricing, name = "pricing"),
    # Contains the view link to the pricing page
    path("about/", views.aboutMe, name = "aboutMe"),

    # Contains the view link to the user's homepage
    path("home/", views.portfolioHome, name = "portfolioHome"),
    # Used to change the graph to the user specified stock
    path('returnClosingPrices/', views.returnStockClosingPrices, name='returnClosingPrices'),
    path('get-stock-graph/', views.get_stock_graph, name='get_stock_graph'),
    path('get-stock-articles/', views.getStockArticles, name='get_stock_articles'),
    path('get-stock-predictions/', views.returnPredictionModels, name='get_stock_models'),
    path('get-model-prediction/', views.get_model_prediction, name='get-model-prediction'),
    path('get-stock-values/', views.getStockValues, name='get-stock-values'),
    path('get-analyst-recommendations/', views.returnRecommendations, name='get-analyst-recommendations'),
    path('get-pricetargets/', views.returnPriceTargets, name='get-pricetargets'),
    path('get-ratings/', views.returnStockRatings, name='get-ratings'),
    path('getStockInfo/', views.returnGeneralInfo, name='getStockInfo'),
    path('getOfficeres/', views.returnCompanyOfficers, name='getOfficeres'),
    
    # Different path means that its a subdirectory
    path("idea", views.projectIdea, name = "projectIdea"),
]
