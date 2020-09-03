from django import forms
from .models import ShippingInfo
import re

class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingInfo
        fields = (
            'address1',
            'address2',
            'phone',
            'city',
            'zip',
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        phone_regex = re.findall(r'^\+\d{9,15}$', phone)
        if not phone_regex or len(phone) > 15:
            raise forms.ValidationError("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
        return phone


    def clean_zip(self):
        zip = self.cleaned_data.get("zip")

        if len(str(zip)) > 5:
            raise forms.ValidationError("The zip code must contain 5 digits")
        return zip
