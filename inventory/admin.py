from django.contrib import admin
from .models import Category, Product, Vendor, Customer, Sale, Purchase, Expense, RestockHistory

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(Purchase)
admin.site.register(Expense)
admin.site.register(RestockHistory)