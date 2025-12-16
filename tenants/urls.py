from django.urls import path

from .views import TenantSignUpView

urlpatterns = [
    path('signup/', TenantSignUpView.as_view(), name='tenant-signup'),
]
