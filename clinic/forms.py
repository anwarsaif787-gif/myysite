from django import forms
from django.utils import timezone

from .models import Appointment, ContactMessage
from .utils import available_slots, generate_slots


class AppointmentForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="Leave this field empty",
    )

    class Meta:
        model = Appointment
        fields = ["service", "date", "time", "name", "email", "phone", "message"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.HiddenInput(),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Anything we should know?"}),
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 9852060649"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].empty_label = "Select a service"
        self.fields["date"].widget.attrs["min"] = timezone.localdate().isoformat()
        for field in self.fields.values():
            if field is not self.fields["website"]:
                field.widget.attrs.setdefault("class", "form-input")

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value

    def clean_date(self):
        day = self.cleaned_data["date"]
        today = timezone.localdate()
        if day < today:
            raise forms.ValidationError("Please choose a date in the future.")
        if not generate_slots(day):
            raise forms.ValidationError("The clinic is closed on this day. Please pick another date.")
        return day

    def clean(self):
        cleaned = super().clean()
        day = cleaned.get("date")
        slot = cleaned.get("time")
        if not day or not slot:
            return cleaned
        if slot not in generate_slots(day):
            raise forms.ValidationError("That time is outside our working hours.")
        if slot not in available_slots(day):
            raise forms.ValidationError("Sorry, that time has just been taken. Please choose another slot.")
        return cleaned


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 9852060649"}),
            "subject": forms.TextInput(attrs={"placeholder": "How can we help?"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell us a little about your case"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "website":
                field.widget.attrs.setdefault("class", "form-input")

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value
