from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages
from django.utils import timezone
from .forms import *
from django.contrib.auth.decorators import login_required
from .utils import generate_verification_code, send_verification_email
from .forms import OTPVerificationForm, EmailVerificationForm
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404



def verify_email_step(request):
    """First step of registration: Email verification"""
    email_form = EmailVerificationForm()
    otp_form = OTPVerificationForm()
    
    if request.method == 'POST':
        if 'email' in request.POST:
            # First step: Send OTP
            email_form = EmailVerificationForm(request.POST)
            if email_form.is_valid():
                email = email_form.cleaned_data['email']
                # Check if email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'This email is already registered.')
                    return render(request, 'verify_email_step.html', {
                        'email_form': email_form,
                        'otp_form': otp_form,
                        'otp_sent': False
                    })
                
                # Generate and send OTP
                verification_code = generate_verification_code()
                print(verification_code)
                if send_verification_email(email, verification_code):
                    # Store email and OTP in session
                    request.session['pending_email'] = email
                    request.session['verification_code'] = verification_code
                    # messages.success(request, 'Verification code sent to your email.')
                    return render(request, 'verify_email_step.html', {
                        'email_form': email_form,
                        'otp_form': otp_form,
                        'otp_sent': True,
                        'email': email
                    })
                else:
                    messages.error(request, 'Failed to send verification code. Please try again.')
        else:
            # Second step: Verify OTP
            otp_form = OTPVerificationForm(request.POST)
            if otp_form.is_valid():
                entered_otp = otp_form.cleaned_data['otp']
                stored_otp = request.session.get('verification_code')
                email = request.session.get('pending_email')
                
                if entered_otp == stored_otp:
                    # OTP is correct, proceed to registration form
                    request.session['email_verified'] = True
                    return redirect('register')
                else:
                    messages.error(request, 'Invalid verification code. Please try again.')
    
    return render(request, 'verify_email_step.html', {
        'email_form': email_form,
        'otp_form': otp_form,
        'otp_sent': False
    })

def register_view(request):
    """Second step of registration: User details and password"""
    # Check if email is verified
    if not request.session.get('email_verified'):
        messages.error(request, 'Please verify your email first.')
        return redirect('verify_email_step')
    
    # Get the verified email from session
    verified_email = request.session.get('pending_email')

    # Pass the email as initial data to the form
    if request.method == 'POST':
        form = SignUpForm(request.POST,request.FILES, initial={'email': verified_email})
        if form.is_valid():
            # Set the email from the verified email
            form.instance.email = verified_email
            user = form.save()

            UserProfile.objects.create(
        user=user,
        role=form.cleaned_data.get('role'),
        bio=form.cleaned_data.get('bio'),
        avatar=form.cleaned_data.get('avatar'),
        audio_file=form.cleaned_data.get('audio_file')
    )
            
            # Clear session data
            request.session.pop('pending_email', None)
            request.session.pop('verification_code', None)
            request.session.pop('email_verified', None)
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
    else:
        form = SignUpForm(initial={'email': verified_email})
    
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def discover_view(request):
    sellers = UserProfile.objects.filter(role='seller')
    buyers = UserProfile.objects.filter(role='buyer')
    user_role = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_role = user_profile.role
        except UserProfile.DoesNotExist:
            user_role = None
    
    if user_role == 'seller':
        # Show both sellers and buyers
        context = {
            'sellers': sellers,
            'buyers': buyers,
            'user_role': user_role,
        }
    elif user_role == 'buyer':
        # Show only sellers
        context = {
            'sellers': sellers,
            'buyers': None,
            'user_role': user_role,
        }
    else:
        # Not logged in or no profile, show nothing
        context = {
            'sellers': None,
            'buyers': None,
            'user_role': user_role,
        }
    return render(request, 'discover.html', context)




@login_required(login_url='login')
def chat_view(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, "No order selected for chat.")
        return redirect('orders')

    order = get_object_or_404(Order, id=order_id)
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Only allow buyer or seller to chat
    if user_profile != order.buyer and user_profile != order.service.seller:
        messages.error(request, "You are not authorized to chat for this order.")
        return redirect('orders')

    # Handle new message
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                order=order,
                sender=user_profile,
                message=message_text
            )
            return redirect(f"{request.path}?order_id={order_id}")

    # Get all messages for this order
    messages_list = ChatMessage.objects.filter(order=order).order_by('timestamp')

    return render(request, 'chat.html', {
        'order': order,
        'messages': messages_list,
        'user_profile': user_profile,
    })


@login_required(login_url='login')
def direct_chat_view(request, user_id):
    try:
        other_profile = UserProfile.objects.get(user__id=user_id)
    except UserProfile.DoesNotExist:
        raise Http404("User not found.")
    my_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            DirectChatMessage.objects.create(sender=my_profile, recipient=other_profile, message=message)
    # Get all messages between these two users (both directions)
    messages_qs = DirectChatMessage.objects.filter(
        (models.Q(sender=my_profile) & models.Q(recipient=other_profile)) |
        (models.Q(sender=other_profile) & models.Q(recipient=my_profile))
    ).order_by('timestamp')
    return render(request, 'direct_chat.html', {
        'other_profile': other_profile,
        'messages': messages_qs,
    })

# @login_required(login_url='login')
def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    return render(request, 'login.html')


@login_required(login_url='login')
def orders_view(request):
    return render(request, 'orders.html')


@login_required(login_url='login')
def profile_view(request, id):
    profile = get_object_or_404(UserProfile, id=id)
    return render(request, 'profile.html', {'profile': profile})


@login_required(login_url='login')
def public_profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'public_profile.html', {'profile': profile})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('index')

@login_required(login_url='login')
def update_profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form =UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('public_profile')
    else:
        form =UserProfileForm(instance=profile)
    return render(request, 'public_profile.html', {'form': form})

@login_required(login_url='login')
def place_order_view(request):
    if request.method == 'POST':
        form = PlaceOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.buyer = UserProfile.objects.get(user=request.user)
            order.save()
            messages.success(request, "Order placed successfully!")
            return redirect('orders')
    else:
        form = PlaceOrderForm()
    return render(request, 'place_order.html', {'form': form})