from django import forms
from .models import Product, Order, CustomerProfile


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'address', 'zipcode', 'city','mobile_no')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'mobile_no': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            })}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'title', 'description', 'price', 'image',)
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'price': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200'
            })}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = [
            'first_name', 'last_name', 'address', 'mobileNo', 'photo', 'user'
        ]
