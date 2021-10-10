from django.contrib.auth.views import LoginView, \
    LogoutView, \
    PasswordChangeDoneView, \
    PasswordChangeView, \
    PasswordResetCompleteView, \
    PasswordResetConfirmView, \
    PasswordResetView
from django.urls import path
from . import views


app_name = 'users'


urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='registration/logged_out.html'),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='registration/password_change_form.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'),
        name='reset'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'),
        name='reset_done'
    ),
]
