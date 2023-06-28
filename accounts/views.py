from django.shortcuts import render,redirect
from.forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.storage import default_storage

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
from .forms import EditUserForm
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from orderss.models import Order
from .forms import EditUserForm
# Create your views here.
def register(request):
     if request.user.is_authenticated:
        return redirect('home')
     if request.method == 'POST': 
         form = RegistrationForm(request .POST)
         if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # username = email.split("@")[0]
            username = form.cleaned_data['username']
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password )
            user.phone_number = phone_number
            user.save()
           
            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Registration Successful. Check your mail for activation')
            return redirect('login')
     else:
         form = RegistrationForm()
     context = {
        'form': form,
     }
     return render(request,'accounts/register.html',context)
    
     

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
    
        if user is not None:  
            auth.login(request, user)
            # messages.success(request, 'You are loggedin') 
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request,"You are loggedout.")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! your account is activated. Please login.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation')
        return redirect('register')    

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
              user = Account.objects.get(email__exact=email)
            #   reset password
              current_site = get_current_site(request)
              mail_subject = 'Reset your password'
              message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
              to_email = email
              send_email = EmailMessage(mail_subject, message, to=[to_email])
              send_email.send()
              messages.success(request,'Password reset mail has been sent to your email address.')
              return redirect('login')
        else:
             messages.error(request,'Account doesnot exists.')
             return redirect('forgotPassword')   
    return render(request,'accounts/forgotPassword.html')   

def resetpassword_validate(request,  uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']= uid
        messages.success(request, 'Please reset yor password')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link has been expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid  = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful.')
            return redirect('login')

        else:
            messages.error(request,'Passwords do not match.')
            return redirect('resetPassword')  
    else:
        return render(request,'accounts/resetPassword.html')
    

def dashboard(request):
    orders = Order.objects.order_by('created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count
    context={
        'orders_count':orders_count,
    }
    return render(request, 'accounts/dashboard.html',context)  

def edit_user_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard')  # Replace 'dashboard' with the appropriate URL name for your dashboard view
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'accounts/edit_user_details.html', {'form': form})



  


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            
            return redirect('change_password')  # Redirect to dashboard or any other page
    else:
        form = PasswordChangeForm(request.user)
    
    context = {'form': form}
    return render(request, 'accounts/change_password.html', context)

        
     
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    print(orders)
    context={
        'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

def order_detail(request, order_id):
    return render(request,'accounts/order_detail.html')