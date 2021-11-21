from django.urls import path, re_path

from .views import (
	signup, profileEdit, passUpdate, account_activation_sent_view, account_activate
)

app_name = 'profiles'

urlpatterns = [
	path('', signup, name='profile-signup'),
    path('profile-edit/', profileEdit, name='profile-edit'),
    path('pass-update/', passUpdate, name='pass-update'),
]
urlpatterns += [
	path('account-activation-sent/', account_activation_sent_view, name='account-activation-sent'),
	path('activate/<uidb64>/<token>/',
		account_activate, name='activate'),
]