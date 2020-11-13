from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.conf import settings

# Create your views here.

def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            # messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('users-login')
    else:

        # If user already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})