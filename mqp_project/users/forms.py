from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Form for registering user accounts on Register page, utilizes built-in Django UserCreationForm
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    # Prevent accounts with the same email
    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError("This email is already used for another profile! Consider resetting your password.")
        return self.cleaned_data['email']

    # Prevent accounts with the same username
    def clean_username(self):
        if User.objects.filter(email=self.cleaned_data['username']).exists():
            raise forms.ValidationError("This username is already used for another profile!")
        return self.cleaned_data['username']

    class Meta:
        model = User

        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Username (for convenience, we recommend using your WPI email username)'
        }

# Form for modifying user account on Profile page
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    # Prevent switching email to another account's email
    def clean_email(self):
        if User.objects.exclude(pk=self.instance.pk).filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError("This email is already used for another profile!")
        return self.cleaned_data['email']

    # Prevent switching username to another account's username
    def clean_username(self):
        if User.objects.exclude(pk=self.instance.pk).filter(email=self.cleaned_data['username']).exists():
            raise forms.ValidationError("This username is already used for another profile!")
        return self.cleaned_data['username']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']