from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from django.utils.timezone import now

from django.db.models import Sum


from .models import Event, Ticket, Order, Organizer, EventDashboard, TicketCategory, EventCategory
from .forms import EventForm, TicketBookingForm, OrganizerRegistrationForm, OrganizerLoginForm


# Home Page
def home(request):
    """
    Display the home page with upcoming, trending, and expired events.
    """
    today = timezone.now().date()

    # Events filtering
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
    trending_events = Event.objects.filter(is_trending=True, date__gte=today).order_by('-date')
    expired_events = Event.objects.filter(date__lt=today).order_by('-date')

    context = {
        'upcoming_events': upcoming_events,
        'trending_events': trending_events,
        'expired_events': expired_events,
    }

    return render(request, 'home.html', context)


def events(request):
    """
    Display a list of events with filtering options.
    """
    today = timezone.now().date()
    
    # Get filter parameters
    category_id = request.GET.get('category')
    location = request.GET.get('location')
    search = request.GET.get('search')
    
    # Start with all events
    all_events = Event.objects.all()
    
    # Apply filters
    if category_id:
        all_events = all_events.filter(category_id=category_id)
    
    if location:
        all_events = all_events.filter(location__icontains=location)
        
    if search:
        all_events = all_events.filter(title__icontains=search)
    
    upcoming_events = all_events.filter(date__gte=today).order_by('date')
    trending_events = all_events.filter(is_trending=True, date__gte=today)
    expired_events = all_events.filter(date__lt=today).order_by('-date')
    
    # Get categories for the filter dropdown
    categories = EventCategory.objects.all()

    context = {
        'upcoming_events': upcoming_events,
        'trending_events': trending_events,
        'expired_events': expired_events,
        'categories': categories,
    }
    return render(request, 'events.html', context)


def event_details(request, event_id):
    """
    Display event details and available tickets.
    """
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event)  # Fetch event tickets
    return render(request, 'event_details.html', {'event': event, 'tickets': tickets})


# Ticket Booking
@login_required
def book_ticket(request, event_id):
    """
    Handle ticket booking for an event.
    """
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event)

    if request.method == "POST":
        ticket_id = request.POST.get('ticket_id')
        # Handle empty or invalid quantity
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        total_price = request.POST.get('total_price')
        
        # Validate quantity
        if quantity <= 0:
            messages.error(request, "Quantity must be at least 1.")
            return render(request, "event_details.html", {
                "event": event,
                "tickets": tickets,
            })
        
        # Get the selected ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Validate ticket availability
        if quantity > ticket.available_tickets:
            messages.error(request, f"Only {ticket.available_tickets} tickets available.")
            return render(request, "event_details.html", {
                "event": event,
                "tickets": tickets,
            })
        
        # Validate total price calculation
        calculated_total = ticket.price * quantity
        if total_price:
            try:
                if abs(float(total_price) - calculated_total) > 0.01:  # Allow for small floating point differences
                    messages.error(request, "Price calculation error. Please try again.")
                    return render(request, "event_details.html", {
                        "event": event,
                        "tickets": tickets,
                    })
            except ValueError:
                # If total_price is not a valid number, use calculated total
                total_price = calculated_total
        else:
            # If total_price is not provided, use calculated total
            total_price = calculated_total
        
        # Create the order
        order = Order.objects.create(
            user=request.user,
            event=event,
            ticket=ticket,
            quantity=quantity,
            total_price=total_price,
            payment_status=False
        )
        # Store order ID in session for payment processing
        request.session['order_id'] = order.id
        messages.success(request, "Order created successfully! Please proceed to payment.")
        return redirect("payment")

    return render(request, "event_details.html", {
        "event": event,
        "tickets": tickets,
    })



# Payment Page
@login_required
def payment(request):
    """
    Display payment page with order details.
    """
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "No order found.")
        return redirect('events')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'payment.html', context)


# Order Confirmation Page
@login_required
def confirmation(request):
    """
    Display order confirmation page with QR code.
    """
    # Get order from session
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "No order found.")
        return redirect('events')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Mark order as paid
    order.payment_status = True
    order.save()
    
    # Generate QR code data
    qr_data = f"Ticket ID: {order.id}, Event: {order.event.title}, User: {request.user.email}"
    
    context = {
        'order': order,
        'qr_data': qr_data,
    }
    return render(request, 'confirmation.html', context)


# User Dashboard (For ticket buyers)
@login_required
def dashboard(request):
    """
    Display user dashboard with their purchased tickets.
    """
    orders = Order.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'orders': orders})


# Cart Page
def cart(request):
    """
    Display the shopping cart with items added by the user.
    """
    cart_items = request.session.get("cart", {})
    return render(request, "cart.html", {"cart_items": cart_items})


# Add to Cart
def add_to_cart(request, ticket_id):
    """
    Add a ticket to the shopping cart.
    """
    if request.method == 'POST':
        # Get quantity from POST data
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
    else:
        quantity = 1
        
    ticket = get_object_or_404(Ticket, id=ticket_id)
    cart = request.session.get("cart", {})

    if str(ticket_id) in cart:
        cart[str(ticket_id)]["quantity"] += quantity
    else:
        cart[str(ticket_id)] = {
            "event": ticket.event.title,
            "category": ticket.get_category_display(),
            "price": str(ticket.price),  # Convert to string for JSON serialization
            "quantity": quantity
        }

    request.session["cart"] = cart
    
    # Calculate cart count
    cart_count = sum(item["quantity"] for item in cart.values())
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            "success": True,
            "cart_count": cart_count
        })
    
    messages.success(request, "Ticket added to cart successfully!")
    return redirect("cart")


# Organizer Signup Page
def organizer(request):
    return render(request, 'organizer_signup.html')


@login_required
def organizer_dashboard(request):
    """
    Display organizer dashboard with events, sales, and payment information.
    """
    organizer = request.user

    events = Event.objects.filter(organizer=organizer)

    for event in events:
        total_tickets = Order.objects.filter(event=event).aggregate(total=Sum('quantity'))['total'] or 0
        event.tickets_sold = total_tickets  # Dynamically attach to the event object

    active_events_count = events.count()
    tickets_sold = Order.objects.filter(event__organizer=organizer).aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = Order.objects.filter(event__organizer=organizer, payment_status=True).aggregate(total=Sum('total_price'))['total'] or 0
    event_dashboards = EventDashboard.objects.filter(organizer=organizer)
    payments = Order.objects.filter(event__organizer=organizer)

    context = {
        'active_events_count': active_events_count,
        'tickets_sold': tickets_sold,
        'total_revenue': total_revenue,
        'events': events,
        'event_dashboards': event_dashboards,
        'payments': payments,
    }
    return render(request, 'organizer-dashboard.html', context)


# Create Event Page
@login_required
def create_event(request):
    """
    Handle event creation by organizers.
    """
    categories = EventCategory.objects.all()

    if request.method == 'POST':
        name = request.POST.get('event_name')
        date = request.POST.get('event_date')
        time = request.POST.get('event_time')
        location = request.POST.get('event_location')
        max_attendees = request.POST.get('max_attendees')
        contact = request.POST.get('contact')
        description = request.POST.get('event_description')
        image = request.FILES.get('event_image')
        price = request.POST.get('price')
        category_id = request.POST.get('category')

        # Validate category
        if not category_id:
            messages.error(request, "Please select a category for the event.")
            return render(request, 'create_event.html', {'categories': categories})
            
        selected_category = get_object_or_404(EventCategory, id=category_id)

        if 'publish' in request.POST:
            status = 'upcoming'
        elif 'draft' in request.POST:
            status = 'draft'
        else:
            status = 'draft'  # default fallback

        # Save event
        event = Event.objects.create(
            organizer=request.user,
            title=name,
            date=date,
            time=time,
            location=location,
            max_attendees=max_attendees if max_attendees else None,
            contact=contact,
            description=description,
            image=image,
            status=status,
            price=price if price else 0,
            category=selected_category
        )

        # Handle ticket categories
        ticket_types = request.POST.getlist('ticket_type[]')
        ticket_prices = request.POST.getlist('ticket_price[]')
        ticket_quantities = request.POST.getlist('ticket_quantity[]')

        for t_type, price, qty in zip(ticket_types, ticket_prices, ticket_quantities):
            if t_type and price and qty:
                TicketCategory.objects.create(
                    event=event,
                    name=t_type,
                    price=price,
                    quantity=qty
                )

        messages.success(request, f"Event '{event.title}' created successfully!")
        return redirect('organizer_dashboard')

    return render(request, 'create_event.html', {'categories': categories})



@login_required
def edit_event(request, event_id):
    """
    Handle event editing by organizers.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect('organizer_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    """
    Handle event deletion by organizers.
    """
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f"Event '{event_title}' deleted successfully!")
        return redirect('organizer_dashboard')
    return render(request, 'confirm_delete.html', {'event': event})


# User Registration
def register_view(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome {user.name or user.email}! Your account has been created successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrganizerRegistrationForm()
    return render(request, 'register.html', {'form': form})
def login_view(request):
    """
    Handle user login.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.name or user.email}!")
            if user.is_superuser:
                return redirect("/admin/")
            elif user.is_premium:
                return redirect("organizer_dashboard")
            else:
                return redirect("dashboard")  # for customers
        else:
            messages.error(request, "Invalid credentials")
            return render(request, "login.html")

    return render(request, "login.html")


# User Logout
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")


def organizer_login(request):
    """
    Handle organizer login.
    """
    if request.method == 'POST':
        form = OrganizerLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data['email'],
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



def organizer_logout(request):
    """
    Handle organizer logout.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('organizer_login')


def organizer_signup(request):
    """
    Handle organizer signup.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("organizer_signup")

        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            phone=phone,
            is_premium=True  # Organizers should be premium by default
        )

        login(request, user)  # Automatically log in the user
        messages.success(request, f"Welcome {user.name}! Your organizer account has been created successfully.")

        return redirect("organizer_dashboard")  # Redirect to dashboard

    return render(request, "organizer_signup.html")


def rates_page(request):
    """
    Display the rates page.
    """
    return render(request, "rates.html")


@login_required
def download_ticket(request, order_id):
    """
    Generate and download ticket as PDF.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Generate QR code data
    qr_data = f"Ticket ID: {order.id}, Event: {order.event.title}, User: {request.user.email}"
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{order.id}.pdf"'
    
    # Create PDF document
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    import io
    import requests
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add ticket information
    p.drawString(100, height - 100, f"Event: {order.event.title}")
    p.drawString(100, height - 120, f"Ticket Type: {order.ticket.get_category_display()}")
    p.drawString(100, height - 140, f"Quantity: {order.quantity}")
    p.drawString(100, height - 160, f"Total Paid: Ksh {order.total_price}")
    
    # Add QR code
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}"
    try:
        qr_image = ImageReader(io.BytesIO(requests.get(qr_url).content))
        p.drawImage(qr_image, 100, height - 300, width=100, height=100)
    except:
        p.drawString(100, height - 300, "QR Code could not be generated")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    
    return response


@login_required
def update_cart(request, ticket_id, change):
    """
    Update the quantity of a ticket in the cart.
    """
    if request.method == 'POST':
        cart = request.session.get("cart", {})
        ticket_id = str(ticket_id)
        
        if ticket_id in cart:
            cart[ticket_id]["quantity"] = max(1, cart[ticket_id]["quantity"] + int(change))
            
            # Remove item if quantity is 0
            if cart[ticket_id]["quantity"] == 0:
                del cart[ticket_id]
                
            request.session["cart"] = cart
            
        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False})


@login_required
def remove_from_cart(request, ticket_id):
    """
    Remove a ticket from the cart.
    """
    if request.method == 'POST':
        cart = request.session.get("cart", {})
        ticket_id = str(ticket_id)
        
        if ticket_id in cart:
            del cart[ticket_id]
            request.session["cart"] = cart
            
        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False})
