from django.shortcuts import render, redirect
import datetime
from carts.models import CartItem, Cart
from .forms import OrderForm
from .models import Payment,Order
import razorpay
from django.conf import settings
from django.http import HttpResponse
# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user
    print(current_user)
    # cart_items = CartItem.objects.filter(user=current_user)
    cart_items = CartItem.objects.all()
    cart_count = cart_items.count()
    
    # if cart_count <= 0:
    #     return redirect('checkout')
    print(total)
    print(quantity)
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
             
            data = Order()
            data.user = current_user
            data.first_name =form.cleaned_data['first_name']
            data.last_name =form.cleaned_data['last_name']
            data.email =form.cleaned_data['email']
            data.phone_number =form.cleaned_data['phone_number']
            data.address_line_1 =form.cleaned_data['address_line_1']
            data.address_line_2 =form.cleaned_data['address_line_2']
            data.state =form.cleaned_data['state']
            data.city =form.cleaned_data['city']
            data.order_note =form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
             
            data.save()
             
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,mt)
            current_date =d.strftime("%Y%d%m")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            print(cart_items)

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment = client.order.create({'amount':int(grand_total)*100, 'currency': 'INR', 'payment_capture': 1})
            
            print('******')
            print(payment)
            print('**********')
            print(total)
            print(tax)
            print(grand_total)
            context ={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'payment': payment,
            }
            return render(request,'orders/payment.html',context)  
            
    else:
        return redirect('home')  
    
     
def payment(request):
    return render(request,'orders/payment.html')    

def success(request):
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    amount_paid = request.GET.get('amount_paid')

    print("razorpay_order_id:", razorpay_order_id)
    print("razorpay_payment_id:", razorpay_payment_id)
    print("amount_paid:", amount_paid)

    try:
        payment = Payment.objects.create(
            user=request.user,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            amount_paid=amount_paid,
        )

        # # Get the corresponding order based on the order_id
        # order = Order.objects.get(order_number=order_id)
        # order.payment = payment  # Assign the payment to the order's payment field
        # order.is_ordered = True  # Mark the order as paid/ordered
        # order.save()

        return HttpResponse('Payment Success!!!!!!')
    except Payment.DoesNotExist:
        return HttpResponse('Payment not found')