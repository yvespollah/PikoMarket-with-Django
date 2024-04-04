from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart,CartItem
from carts.views import _cart_id
import requests
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0] 
            
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username ,password=password)
            user.phone_number = phone_number
            user.save()
            form = RegistrationForm()
            messages.success(request, 'Registration Successful')
            return redirect('register')
    else:        
        form = RegistrationForm() 
    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_existe = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_existe:
                    cart_item = CartItem.objects.filter(cart=cart)
                    print('varier')
                    # getting product variation by cart id
                    product_variation = []
                    for item in cart_item:   
                        variation  = item.variations.all()
                        product_variation.append(list(variation))
                        
                    # get cart item from the user to acces his product variation    
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pr in product_variation:
                        if pr in existing_variation_list:
                            print('there s varie')
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            print('no varie')
                            cart_item=CartItem.objects.filter(cart=cart)    
                            for item in cart_item:
                                item.user=user
                                item.save()
                       
            except:...    
            auth.login(request,user)
            messages.success(request, 'You are now Logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params= dict(x.split('=') for x in query.split('&')) 
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('dashboard')    
        else:
            messages.error(request, 'Invalid login information')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are Logged out')
    return redirect('login')

@login_required(login_url = 'login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')