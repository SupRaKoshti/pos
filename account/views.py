from django.shortcuts import render
from django.contrib.auth.views import LoginView

from rest_framework import generics
from rest_framework.permissions import AllowAny

from account.models import CustomUser
from account.serializers import CustomUserSerializer

def register(request):
    if request.method == 'POST':
        # Handle registration logic here
        pass
    return render(request, 'account/register.html')

class RoleBaseLoginRedict(LoginView):
    def get_success_url(self):

        user = self.request.user

        if user.role == 'admin':
            return '/admin/'
        elif user.role == 'manager':
            return '/dashboard/'
        elif user.role == 'stockp_manager':
            return '/dashboard/'
        elif user.role == 'sales_manager':
            return '/dashboard/'
        elif user.role == 'accountant':
            return '/dashboard/'
        elif user.role == 'cashier':
            return '/pos/'
        else:
            return '/account/login/'
        
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
