from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events', views.events, name='events'),
    path('event-details/<int:event_id>/', views.event_details, name='event_details'),
    path('book-ticket/<int:event_id>/', views.book_ticket, name='book_ticket'),
    path('payment', views.payment, name='payment'),
    path('confirmation', views.confirmation, name='confirmation'),
    path('dashboard', views.dashboard, name='dashboard'),  # customer
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),

    # Organizer
    path('organizer', views.organizer, name='organizer'),
    path('organizer-dashboard', views.organizer_dashboard, name='organizer_dashboard'),
    path('organizer-login', views.organizer_login, name='organizer_login'),
    path('organizer-logout', views.organizer_logout, name='organizer_logout'),
    path('signup', views.organizer_signup, name='organizer_signup'),

    # Events
    path('create-event', views.create_event, name='create_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),

    # Cart
    path('cart', views.cart, name='cart'),
    path('add-to-cart/<int:ticket_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:ticket_id>/<int:change>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:ticket_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('download-ticket/<int:order_id>/', views.download_ticket, name='download_ticket'),


    path("rates/", views.rates_page, name="rates_page"),

    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
