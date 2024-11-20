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
    
    
    # Different path means that its a subdirectory
    path("idea", views.projectIdea, name = "projectIdea"),
]
