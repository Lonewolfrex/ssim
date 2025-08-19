from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='product_list', permanent=True)),  # Redirect root to products/
    path('', include('inventory.urls')),  # Your app urls
]
