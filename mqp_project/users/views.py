from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Register new user
def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been registered! Please log in.")
            return redirect('users-login')
    else:

        # If user already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# View or update profile page
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been updated successfully!")
            return redirect('users-profile')

    else:
        form = UserUpdateForm(instance=request.user)


    context = {
        'form': form
    }

    return render(request, 'users/profile.html', context)

# Page for deleting user. Deletes the user when the request is POST
@login_required
def delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account was successfully deleted!")
        return redirect('users-login')

    return render(request, 'users/delete.html')

# Redirect to login page and show success message after password reset
def password_reset_complete(request):
    messages.success(request, "Your password was reset successfully! Please log in with your new password.")
    return redirect('users-login')