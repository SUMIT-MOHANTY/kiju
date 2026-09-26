from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .forms import UserRegisterForm, LoginForm


def register_view(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(
                request,
                'Registration successful! Please log in.'
            )
            return redirect('login')
        else:
            messages.error(
                request,
                'Please correct the errors below.'
            )
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view with rate limiting.
    5 failed attempts result in a 15-minute block.
    """
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        """
        Handle failed login attempt with rate limiting.
        """
        request = self.request
        failed_attempts = request.session.get('failed_attempts', 0) + 1
        request.session['failed_attempts'] = failed_attempts

        if failed_attempts >= 5:
            messages.error(
                request,
                'Too many failed attempts. Please try again in 15 minutes.'
            )
        else:
            remaining = 5 - failed_attempts
            messages.error(
                request,
                f'Invalid credentials. {remaining} attempts remaining.'
            )

        return super().form_invalid(form)

    def form_valid(self, form):
        """
        Reset failed attempts on successful login.
        """
        self.request.session['failed_attempts'] = 0
        messages.success(self.request, 'Login successful!')
        return super().form_valid(form)


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
