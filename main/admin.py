from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Event, Ticket, Order, EventCategory, Organizer

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

class EventAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

admin.site.register(Event, EventAdmin)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(EventCategory)
admin.site.register(Organizer)