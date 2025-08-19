from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Customer, Vendor, Expense, Sale, Category, RestockHistory
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .forms import SaleForm, CategoryForm, ProductForm
def products_list(request):
    products = Product.objects.all()
    return render(request, 'products_list.html', {'products': products})

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

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            # Add initial restock history if restock_date and stock_quantity given
            if product.restock_date and product.stock_quantity:
                RestockHistory.objects.create(
                    product=product,
                    previous_stock=0,
                    restocked_quantity=product.stock_quantity,
                    restock_date=product.restock_date
                )
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    old_stock = product.stock_quantity
    old_restock_date = product.restock_date
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated_product = form.save(commit=False)
            # Check for restock changes
            if updated_product.stock_quantity > old_stock or updated_product.restock_date != old_restock_date:
                restocked_qty = max(updated_product.stock_quantity - old_stock, 0)
                if restocked_qty > 0:
                    RestockHistory.objects.create(
                        product=updated_product,
                        previous_stock=old_stock,
                        restocked_quantity=restocked_qty,
                        restock_date=updated_product.restock_date or old_restock_date
                    )
            updated_product.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'product': product})

def restock_history_list(request, pk):
    product = get_object_or_404(Product, pk=pk)
    history = product.restock_histories.all().order_by('-restock_date')
    return render(request, 'restock_history_list.html', {'product': product, 'history': history})