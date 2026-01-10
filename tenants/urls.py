from django.urls import path

from .views import TenantSignUpView, TenantSignInView, TenantListView

urlpatterns = [
    path('signup/', TenantSignUpView.as_view(), name='tenant-signup'),
    path('signin/', TenantSignInView.as_view(), name='tenant-signin'),
    path('list/', TenantListView.as_view(), name="tenant-list")
]
