from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.utils.timezone import now

from .models import Event, Ticket, Order, Organizer
from .forms import EventForm, TicketBookingForm, OrganizerSignUpForm, OrganizerLoginForm


# Home Page
def home(request):
    return render(request, 'home.html')


# List of Events
# def events(request):
#     all_events = Event.objects.all()
#     category = request.GET.get('category')
#     location = request.GET.get('location')
#
#     if category and category != "Category":
#         all_events = all_events.filter(category=category)
#
#     if location and location != "Location":
#         all_events = all_events.filter(location=location)
#
#     upcoming_events = all_events.filter(date__gte=now()).order_by("date")
#     expired_events = all_events.filter(date__lt=now()).order_by("-date")
#
#     return render(request, 'events.html', {
#         'upcoming_events': upcoming_events,
#         'expired_events': expired_events
#     })

def events(request):
    today = timezone.now().date()

    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
    trending_events = Event.objects.filter(is_trending=True, date__gte=today)
    expired_events = Event.objects.filter(date__lt=today).order_by('-date')

    context = {
        'upcoming_events': upcoming_events,
        'trending_events': trending_events,
        'expired_events': expired_events,
    }
    return render(request, 'events.html', context)


# Event Details
def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event)  # Fetch event tickets
    return render(request, 'event_details.html', {'event': event, 'tickets': tickets})


# Ticket Booking
@login_required
def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event)

    if request.method == "POST":
        form = TicketBookingForm(request.POST, event=event)  # ✅ Pass event
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.event = event
            order.total_price = order.quantity * order.ticket.price
            order.save()
            return redirect("payment")  # or pass ticket ID to payment page
    else:
        form = TicketBookingForm(event=event)  # ✅ Also here

    return render(request, "event_details.html", {
        "form": form,
        "event": event,
        "tickets": tickets,
    })



# Payment Page
@login_required
def payment(request):
    return render(request, 'payment.html')


# Order Confirmation Page
@login_required
def confirmation(request):
    return render(request, 'confirmation.html')


# User Dashboard (For ticket buyers)
@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'orders': orders})


# Cart Page
def cart(request):
    cart_items = request.session.get("cart", {})
    return render(request, "cart.html", {"cart_items": cart_items})


# Add to Cart
def add_to_cart(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    cart = request.session.get("cart", {})

    if str(ticket_id) in cart:
        cart[str(ticket_id)]["quantity"] += 1
    else:
        cart[str(ticket_id)] = {
            "event": ticket.event.title,
            "category": ticket.get_category_display(),
            "price": ticket.price,
            "quantity": 1
        }

    request.session["cart"] = cart
    return redirect("cart")


# Organizer Signup Page
def organizer(request):
    return render(request, 'organizer_signup.html')


# Organizer Dashboard (For event managers)
@login_required
def organizer_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    events = Event.objects.filter(organizer=request.user)
    return render(request, "organizer-dashboard.html", {"events": events})


# Create Event Page
@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Assign logged-in user as the organizer
            event.save()
            return redirect("organizer_dashboard")  # Redirect to organizer dashboard
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('organizer_dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.delete()
    return redirect('organizer_dashboard')


# User Registration
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


# User Logout
def logout_view(request):
    logout(request)
    return redirect("home")


def organizer_login(request):
    if request.method == 'POST':
        form = OrganizerLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user and user.is_premium:
                login(request, user)
                messages.success(request, "Welcome to your organizer dashboard.")
                return redirect('organizer_dashboard')
            else:
                messages.error(request, "Invalid credentials or not a premium organizer.")
    else:
        form = OrganizerLoginForm()
    return render(request, 'organizer_login.html', {'form': form})


@login_required
def organizer_dashboard(request):
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'organizers/dashboard.html', {'events': events})


def organizer_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('organizer_login')


def organizer_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("organizer_signup")

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        # Create Organizer Profile
        Organizer.objects.create(user=user, phone=phone)

        # Auto-login the organizer after signup
        login(request, user)
        messages.success(request, "Signup successful! Welcome to your dashboard.")
        return redirect("organizer_dashboard")

    return render(request, "organizer_signup.html")
