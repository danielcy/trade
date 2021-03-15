"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from web.service.playback_service import *
from web.service.selector_service import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('playback/launch', run_playback),
    path('playback/get_result', get_playback_result),
    path('selector/get_selectors', get_selectors),
    path('selector/launch', launch_selector),
    path('selector/get_result', get_selector_result),
]
