from django import forms
from django.forms import inlineformset_factory
from .models import Sale, Category, Product, Vendor, Customer, SaleItem   

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['payment_method', 'transaction_date']

SaleItemFormset = inlineformset_factory(
    Sale, SaleItem,
    fields=['product', 'quantity', 'amount_paid'],
    extra=1, can_delete=True,
)

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
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone_number', 'address']
   
class CustomerSelectionForm(forms.Form):
    CHOICE_EXISTING = 'existing'
    CHOICE_NEW = 'new'
    CUSTOMER_CHOICES = [
        (CHOICE_EXISTING, 'Select Existing Customer'),
        (CHOICE_NEW, 'Add New Customer'),
    ]

    customer_choice = forms.ChoiceField(
        choices=CUSTOMER_CHOICES,
        widget=forms.RadioSelect,
        initial=CHOICE_EXISTING,
        label="Customer Type"
    )
    existing_customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        label="Select Customer"
    )
    # Fields for new customer
    name = forms.CharField(required=False, label="Name")
    phone_number = forms.CharField(required=False, label="Phone Number")
    address = forms.CharField(widget=forms.Textarea, required=False, label="Address")


