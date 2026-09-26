from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserRegisterForm(forms.ModelForm):
    """
    Form for user registration with email uniqueness, username uniqueness,
    and password complexity validation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        label=_('Password')
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label=_('Confirm Password')
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'Enter username'}
            ),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    _('A user with this email already exists.')
                )
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username__iexact=username).exists():
                raise ValidationError(
                    _('A user with this username already exists.')
                )
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError(
                    _('Password must be at least 8 characters long.')
                )
            if not any(char.isdigit() for char in password):
                raise ValidationError(
                    _('Password must contain at least one digit.')
                )
            if not any(char.isupper() for char in password):
                raise ValidationError(
                    _('Password must contain at least one uppercase letter.')
                )
            if not any(char.islower() for char in password):
                raise ValidationError(
                    _('Password must contain at least one lowercase letter.')
                )
            if not any(char.isdigit() for char in password):
                raise ValidationError(
                    _('Password must contain at least one digit.')
                )
                raise ValidationError(
                    _('Password must contain at least one special character.')
                )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError(_('Passwords do not match.'))

        return cleaned_data


class LoginForm(AuthenticationForm):
    """
    Custom login form with email-based authentication.
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-input'
        }),
        label=_('Email')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-input'
        }),
        label=_('Password')
    )
