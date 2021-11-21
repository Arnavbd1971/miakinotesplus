from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.views.generic import UpdateView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model

from .forms import SignUpForm, UpdateUserForm, UpdatePassForm
from .models import Profile
from .utils import get_location_from_ip
from .tokens import account_activation_token

from django.contrib.auth.decorators import login_required
from django.contrib import messages


User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.location = form.cleaned_data.get('location')
            ip_address = user.profile.location
            location = get_location_from_ip(ip_address)
            print(location)
            user.profile.location = location
            user.save()
            current_site = get_current_site(request)
            subject = "Activate your Django Serives Account"
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user)
            })
            user.email_user(subject, message)
            return redirect('profiles:account-activation-sent')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {
        'form': form,
        'profile': True
    })


def account_activation_sent_view(request):
    return render(request, 'registration/account_activation_sent.html')


def account_activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(e)
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('users:my_notes')
    else:
        return render(request, 'registration/account_activation_invalid.html')

@login_required
def profileEdit(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profiles:profile-edit')
    else:
        user_form = UpdateUserForm(instance=request.user)

    return render(request, 'app/profile_edit.html', {'form': user_form})

@login_required
def passUpdate(request):
    if request.method == 'POST':
        form = UpdatePassForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password is updated successfully, Please login again.')
            return redirect('profiles:pass-update')
    else:
        form = UpdatePassForm(user=request.user)
    return render(request, 'app/pass_update.html', {'form': form})

