from django.urls import path
from .views import home_view, signup_view, my_notes_view
app_name = "users"
urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='sign-up'),
    path('my_notes/', my_notes_view, name='my_notes'),
]