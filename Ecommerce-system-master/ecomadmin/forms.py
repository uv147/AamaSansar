from django import forms

from ecomadmin.models import Banner, About
from store.models import Category, OrderItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'title'
        ]


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            'title', 'caption', 'image', 'weight'
        ]


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = [
            'title', 'description', 'logo', 'photo', 'phoneNo', 'mobileNo', 'address'
        ]
