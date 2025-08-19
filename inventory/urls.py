from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('charts/', views.capex_opex_charts, name='capex_opex_charts'),
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/new/', views.sale_create, name='sale_create'),
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/new/', views.category_create, name='category_create'),
]
