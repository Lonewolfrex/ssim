from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    gstin = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField(blank=True, null=True)  # Optional email
    phone_number  = models.CharField(max_length=20, unique=False)     # Make phone unique for searching
    address = models.TextField(blank=True)                    # Make address optional

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    restock_date = models.DateField(blank=True, null=True)  # New field for the latest restock date

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Sale {self.product.name} to {self.customer.name}"

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Purchase {self.product.name} from {self.vendor.name}"

class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = (
        ('CAPEX', 'Capital Expenditure'),
        ('OPEX', 'Operational Expenditure')
    )
    type = models.CharField(max_length=5, choices=EXPENSE_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.type}: {self.description} - {self.amount}"

class RestockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='restock_histories')
    previous_stock = models.PositiveIntegerField()
    restocked_quantity = models.PositiveIntegerField()
    restock_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Restocked {self.restocked_quantity} {self.product.name} on {self.restock_date}"
    
class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    transaction_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.customer.name} - {self.transaction_date.date()}"
    
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)  # price per item * quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Sale #{self.sale.id}"
