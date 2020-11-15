from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm
from django.conf import settings
from django.contrib.auth.decorators import login_required

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

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('users-profile')

    else:
        form = UserUpdateForm(instance=request.user)


    context = {
        'form': form
    }

    return render(request, 'users/profile.html', context)

@login_required
def delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('users-login')

    return render(request, 'users/delete.html')