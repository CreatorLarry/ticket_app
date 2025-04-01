"""
URL configuration for ticket_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events', views.events, name='events'),
    path('event-details', views.event_details, name='event_details'),
    path('payment', views.payment, name='payment'),
    path('confirmation', views.confirmation, name='confirmation'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('cart', views.cart, name='cart'),
    path('organizer', views.organizer, name='organizer'),
    path('organizer-dashboard', views.organizer_dashboard, name='organizer_dashboard'),
    path('create-event', views.create_event, name='create_event'),
    path('admin/', admin.site.urls),
]
