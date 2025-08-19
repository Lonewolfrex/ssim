from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('charts/', views.capex_opex_charts, name='capex_opex_charts'),
]
