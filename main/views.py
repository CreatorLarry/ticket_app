from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')


def events(request):
    return render(request, 'events.html')


def event_details(request):
    return render(request, 'event_details.html')


def payment(request):
    return render(request, 'payment.html')


def confirmation(request):
    return render(request, 'confirmation.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def cart(request):
    return render(request, 'cart.html')


def organizer(request):
    return render(request, 'organizer_signup.html')


def organizer_dashboard(request):
    return render(request, 'organizer-dashboard.html')


def create_event(request):
    return render(request, 'create_event.html')