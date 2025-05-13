from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Event, Ticket, Order, Organizer


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "date", "time", "location", "image", "category"]


class TicketBookingForm(forms.Form):
    ticket = forms.ModelChoiceField(queryset=Ticket.objects.none(), label="Select Ticket Type")

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        if event:
            self.fields['ticket'].queryset = Ticket.objects.filter(event=event)


class OrganizerSignUpForm(UserCreationForm):
    class Meta:
        model = Organizer
        fields = ['email', 'name', 'phone', 'password1', 'password2']


class OrganizerLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class EventFormDashboard(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'status']
