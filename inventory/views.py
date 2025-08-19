from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Customer, Vendor, Expense, Sale, Category
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .forms import SaleForm, CategoryForm
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'vendors': vendors})

def capex_opex_charts(request):
    # Example: Aggregate monthly CAPEX and OPEX for last 12 months
    import calendar
    from django.db.models.functions import TruncMonth

    expenses = Expense.objects.annotate(month=TruncMonth('date'))\
        .values('month', 'type')\
        .annotate(total=Sum('amount'))\
        .order_by('month')

    # Prepare data for chart
    months = []
    capex_data = []
    opex_data = []

    month_set = sorted(set([expense['month'] for expense in expenses]))
    for month in month_set:
        months.append(month.strftime("%b %Y"))
        capex_sum = sum(e['total'] for e in expenses if e['month'] == month and e['type'] == 'CAPEX')
        opex_sum = sum(e['total'] for e in expenses if e['month'] == month and e['type'] == 'OPEX')
        capex_data.append(float(capex_sum))
        opex_data.append(float(opex_sum))

    context = {
        'months': months,
        'capex_data': capex_data,
        'opex_data': opex_data,
    }
    return render(request, 'capex_opex_charts.html', context)

# Sales list & create
def sales_list(request):
    sales = Sale.objects.select_related('product', 'customer').all().order_by('-sale_date')
    return render(request, 'sales_list.html', {'sales': sales})

def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_list')
    else:
        form = SaleForm()
    return render(request, 'sale_form.html', {'form': form})

# Categories list & create
def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'categories_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})
