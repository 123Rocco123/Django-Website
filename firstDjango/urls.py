"""
URL configuration for firstDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from register import views as registerViews

urlpatterns = [
    # Used to access the "urls" folder in the firstApp folder
        # This folder has to be created as its not added by default
        # When adding a path, we specify 
    path('', include("firstApp.urls")),
    path('firstApp/', include("firstApp.urls")),
    path("register/", registerViews.register, name = "register"),
    path("logout/", registerViews.logout_user, name = "logout"),
    
    path('admin/', admin.site.urls),

    # Page used for the authentication
        # Uses the defualt Django login/register/... templates
    path("", include("django.contrib.auth.urls")),
]
