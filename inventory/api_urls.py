from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProductViewSet, CategoryViewSet, VendorViewSet,
    CustomerViewSet, SaleViewSet, ExpenseViewSet, ProductBulkCreateView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'vendors', VendorViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/products/bulk/', ProductBulkCreateView.as_view(), name='product-bulk-create'),
]
