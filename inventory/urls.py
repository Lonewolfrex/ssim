from django.urls import path
from . import views
from .views import create_sale, sales_list, sale_detail

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('charts/', views.capex_opex_charts, name='capex_opex_charts'),
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/new/', views.create_sale, name='create_sale'),
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('products/', views.products_list, name='products_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/restock-history/', views.restock_history_list, name='restock_history_list'),
    path('sales/new/', create_sale, name='create_sale'),
    path('sales/', sales_list, name='sales_list'),
    path('sales/<int:pk>/', sale_detail, name='sale_detail'),
]
