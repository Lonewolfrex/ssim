from django import forms
from .models import Sale, Category

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'customer', 'quantity', 'sale_price', 'discount']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
