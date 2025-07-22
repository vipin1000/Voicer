from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages
from django.utils import timezone
from .forms import *
from django.contrib.auth.decorators import login_required




def register_view(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'You are Registered')
            return redirect('indes')
        else:
            form = SignUpForm()
            return render(request, 'register.html', {'form':form})
      
    return render(request, 'register.html',{'form':form})




@login_required
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




@login_required
def admin_view(request):
    return render(request, 'admin.html')


@login_required
def chat_view(request):
    return render(request, 'chat.html')



@login_required
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


@login_required
def orders_view(request):
    return render(request, 'orders.html')


@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def public_profile_view(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)
    return render(request, 'public_profile.html', {'profile': profile})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged in successfully!')
    return redirect('login')
