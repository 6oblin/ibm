from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User, Item


class UserRegistrationForm(UserCreationForm):
    """Custom registration form that works with our custom User model"""
    
    class Meta:
        model = User
        fields = ('username',)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'quantity', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price', 'step': '0.01'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise ValidationError("Item name must be at least 2 characters long.")
        return name.strip()
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        if quantity is not None and quantity > 10000:
            raise ValidationError("Quantity cannot exceed 10,000.")
        return quantity
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError("Price cannot be negative.")
        if price is not None and price > 1000000:
            raise ValidationError("Price cannot exceed 1,000,000.")
        return price

