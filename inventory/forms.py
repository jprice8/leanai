from django import forms
from .models import Item, Order, Usage


class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_qty']


class UsageForm(forms.ModelForm):
    class Meta:
        model = Usage
        fields = ['usage_qty']