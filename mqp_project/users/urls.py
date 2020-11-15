from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='users-register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True), name='users-login'),
    path('logout/', auth_views.logout_then_login, name='users-logout'),
    path('profile/', views.profile, name='users-profile'),
    path('delete/', views.delete, name='users-delete'),
    # path('password_reset/',
    #      auth_views.PasswordResetView.as_view(
    #          template_name='users/password_reset.html'
    #      ),
    #      name='users/password_reset'),
    # path('password-reset/done/',
    #      auth_views.PasswordResetDoneView.as_view(
    #          template_name='users/password_reset_done.html'
    #      ),
    #      name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',
    #      auth_views.PasswordResetConfirmView.as_view(
    #          template_name='users/password_reset_confirm.html'
    #      ),
    #      name='password_reset_confirm'),
    # path('password-reset-complete/',
    #      auth_views.PasswordResetCompleteView.as_view(
    #          template_name='users/password_reset_complete.html'
    #      ),
    #      name='password_reset_complete'),
]