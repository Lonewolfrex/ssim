from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Customer, Vendor, Expense, Sale, Category, RestockHistory, SaleItem
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from .forms import SaleForm, CategoryForm, ProductForm, SaleItemFormset, CustomerForm, CustomerSelectionForm
from django.core.paginator import Paginator
from django.db import transaction
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product, Category
from django.forms import formset_factory
from django.contrib import messages

def products_list(request):
    products = Product.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    sort_by = request.GET.get('sort', 'name')
    allowed_sort_fields = [
        'name', 'category__name', 'vendor__name', 'stock_quantity',
        'cost_price', 'mrp', 'selling_price', 'discount', 'restock_date'
    ]
    # Validate sort field including descending prefix '-'
    if sort_by.lstrip('-') not in allowed_sort_fields:
        sort_by = 'name'

    products = products.order_by(sort_by)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id or '',
        'sort_by': sort_by,
        'search_query': search_query or '',
    }
    return render(request, 'products_list.html', context)

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
    sales = Sale.objects.all().order_by('-transaction_date')

    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sales/sales_list.html', {'page_obj': page_obj})

def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_list')
    else:
        form = SaleForm()
    return render(request, 'sale_form.html', {'form': form})

def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/sale_detail.html', {'sale': sale})


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

def create_sale(request):
    if request.method == 'POST':
        customer_form = CustomerSelectionForm(request.POST)
        sale_form = SaleForm(request.POST)
        sale_item_formset = SaleItemFormset(request.POST)

        if customer_form.is_valid() and sale_form.is_valid() and sale_item_formset.is_valid():
            try:
                with transaction.atomic():
                    choice = customer_form.cleaned_data['customer_choice']
                    if choice == customer_form.CHOICE_NEW:
                        name = customer_form.cleaned_data['name']
                        phone = customer_form.cleaned_data['phone_number']
                        address = customer_form.cleaned_data['address']
                        if not all([name, phone]):
                            messages.error(request, "Name and Phone number are required for new customer")
                            raise ValueError("Missing customer info")
                        customer, created = Customer.objects.get_or_create(
                            phone_number=phone,
                            defaults={'name': name, 'address': address}
                        )
                    else:
                        customer = customer_form.cleaned_data['existing_customer']
                        if not customer:
                            messages.error(request, "Please select an existing customer or add a new one")
                            raise ValueError("No customer selected")

                    sale = sale_form.save(commit=False)
                    sale.customer = customer
                    sale.save()

                    total_amount = 0
                    for form in sale_item_formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                            product = form.cleaned_data.get('product')
                            quantity = form.cleaned_data.get('quantity')
                            amount_paid = form.cleaned_data.get('amount_paid')

                            if product.stock_quantity < quantity:
                                messages.error(request, f"Insufficient stock for {product.name}")
                                raise ValueError("Stock insufficient")

                            product.stock_quantity -= quantity
                            product.save()

                            sale_item = form.save(commit=False)
                            sale_item.sale = sale
                            sale_item.save()

                            total_amount += amount_paid

                    sale.total_amount = total_amount
                    sale.save()

                    messages.success(request, "Sale recorded successfully")
                    return redirect('sales_list')

            except ValueError:
                # Will display error messages above
                pass

        else:
            messages.error(request, "Please fix the errors below.")
    else:
        customer_form = CustomerSelectionForm()
        sale_form = SaleForm()
        sale_item_formset = SaleItemFormset()

    return render(request, 'sales/create_sale.html', {
        'customer_form': customer_form,
        'sale_form': sale_form,
        'sale_item_formset': sale_item_formset,
    })





