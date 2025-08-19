from django import forms
from .models import Sale, Category, Product, Vendor, Customer

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'customer', 'quantity', 'sale_price', 'discount']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'vendor', 'cost_price', 'mrp', 'selling_price',
            'discount', 'stock_quantity', 'image', 'restock_date',
        ]
        widgets = {
            'restock_date': forms.DateInput(attrs={'type': 'date'}),
        }