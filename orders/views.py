from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
import datetime

# Create your views here.
def payments(request):
    return render(request,'orders/payment.html')

def place_order(request,total=0,quantity=0):
    current_user = request.user
    # if the cart count is less than 0 the redirect to shop
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store') 
    
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+= (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax   
    
    if request.method == 'POST':
        form = OrderForm(request.POST) 
        if form.is_valid():
            # store all the relevant information in the dabla
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name'] 
            data.last_name = form.cleaned_data['last_name'] 
            data.phone = form.cleaned_data['phone'] 
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address'] 
            data.city = form.cleaned_data['city'] 
            data.country = form.cleaned_data['country'] 
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") # 20240403
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user = current_user, is_ordered=False,order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total
                    
            }
            return render(request, 'orders/payment.html',context)
        else:
            return redirect('checkout') 
            
   