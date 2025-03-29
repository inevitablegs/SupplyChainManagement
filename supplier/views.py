from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import SupplierRegistrationForm, SupplierLoginForm, BidForm
from .models import Supplier, Bid
from django.contrib.auth.models import User
from manufacturer.models import QuoteRequest, Manufacturer
from django.contrib import messages

# Add at the top
from django.conf import settings
from utils.email import send_email

# Update supplier_register function
def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            
            supplier = Supplier.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                company_name=form.cleaned_data['company_name'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                business_type=form.cleaned_data['business_type'],
                website=form.cleaned_data['website'],
                phone_number=form.cleaned_data['phone_number'],
                key_services=form.cleaned_data['key_services'],
                wallet_address=form.cleaned_data['wallet_address']
            )
            
            # Send welcome email
            send_email(
                subject="Your Supplier Account Has Been Created",
                to_email=user.email,
                template_name="emails/account_created_supplier.html",
                context={
                    'supplier': supplier,
                    'user': user
                }
            )
    else:
        form = SupplierRegistrationForm()
    return render(request, 'supplier/register.html', {'form': form})

def supplier_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Check if this user is a supplier
                try:
                    supplier = Supplier.objects.get(user=user)
                    login(request, user)
                    return redirect('supplier_dashboard')
                except Supplier.DoesNotExist:
                    form.add_error(None, "This account is not registered as a supplier")
    else:
        form = SupplierLoginForm()
    return render(request, 'supplier/login.html', {'form': form})

# supplier/views.py
def supplier_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('supplier_login')
    
    try:
        supplier = Supplier.objects.get(user=request.user)
        open_quotes = QuoteRequest.objects.filter(status='open').order_by('-created_at')
        
        # Category filtering
        category_filter = request.GET.get('category')
        if category_filter:
            open_quotes = open_quotes.filter(category=category_filter)
        
        # Get all unique categories for the filter dropdown
        categories = QuoteRequest.objects.values_list('category', flat=True).distinct()
        
        your_bids = Bid.objects.filter(supplier=supplier).select_related('quote')
        
        return render(request, 'supplier/dashboard.html', {
            'supplier': supplier,
            'open_quotes': open_quotes,
            'your_bids': your_bids,
            'categories': categories,
            'current_category': category_filter
        })
    except Supplier.DoesNotExist:
        return redirect('supplier_login')

# Update submit_bid function
def submit_bid(request, quote_id):
    if not request.user.is_authenticated:
        return redirect('supplier_login')
    
    supplier = get_object_or_404(Supplier, user=request.user)
    quote = get_object_or_404(QuoteRequest, id=quote_id, status='open')
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = Bid.objects.create(
                supplier=supplier,
                quote=quote,
                bid_amount=form.cleaned_data['bid_amount'],
                delivery_time=form.cleaned_data['delivery_time'],
                comments=form.cleaned_data['comments']
            )
            
            # Send bid confirmation to supplier
            send_email(
                subject=f"Your Bid for {quote.product} Has Been Submitted",
                to_email=request.user.email,
                template_name="emails/bid_submitted.html",
                context={
                    'supplier': supplier,
                    'quote': quote,
                    'bid': bid
                }
            )
            
            # Send notification to manufacturer
            send_email(
                subject=f"New Bid Received for {quote.product}",
                to_email=quote.manufacturer.user.email,
                template_name="emails/new_bid_received.html",
                context={
                    'manufacturer': quote.manufacturer,
                    'supplier': supplier,
                    'quote': quote,
                    'bid': bid
                }
            )
            
            messages.success(request, 'Your bid has been submitted successfully!')
            return redirect('supplier_dashboard')
    else:
        form = BidForm()
    
    return render(request, 'supplier/submit_bid.html', {
        'form': form,
        'quote': quote,
        'supplier': supplier
    })
    
    
def view_profile(request):
    if not request.user.is_authenticated:
        return redirect('supplier_login')
    
    supplier = Supplier.objects.get(user=request.user)
    return render(request, 'supplier/profile.html', {'supplier': supplier})

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('supplier_login')
    
    supplier = Supplier.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Update basic fields (no image handling)
        supplier.first_name = request.POST.get('first_name', supplier.first_name)
        supplier.last_name = request.POST.get('last_name', supplier.last_name)
        supplier.company_name = request.POST.get('company_name', supplier.company_name)
        supplier.city = request.POST.get('city', supplier.city)
        supplier.state = request.POST.get('state', supplier.state)
        supplier.business_type = request.POST.get('business_type', supplier.business_type)
        supplier.website = request.POST.get('website', supplier.website)
        supplier.phone_number = request.POST.get('phone_number', supplier.phone_number)
        supplier.key_services = request.POST.get('key_services', supplier.key_services)
        supplier.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('supplier_profile')
    
    return render(request, 'supplier/edit_profile.html', {
        'supplier': supplier
    })
    
def view_manufacturer_profile(request, manufacturer_id):
    if not request.user.is_authenticated:
        return redirect('supplier_login')
    
    try:
        supplier = Supplier.objects.get(user=request.user)
        manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        quote_id = request.GET.get('quote_id')  # Get from URL parameter
        return render(request, 'supplier/manufacturer_profile.html', {
            'manufacturer': manufacturer,
            'supplier': supplier,
            'quote_id': quote_id
        })
    except Manufacturer.DoesNotExist:
        messages.error(request, "Manufacturer not found")
        return redirect('supplier_dashboard')