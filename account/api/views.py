# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Don't override username_field - keep it as 'username'
    # Instead, add email field and handle the conversion
    
    email = serializers.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username not required since we'll use email
        self.fields['username'].required = False
    
    def validate(self, attrs):
        # Get email and password from the request data
        email = attrs.get('email')
        password = attrs.get('password')
        
        print(f"🔍 [DEBUG] Validating login for email: {email}")
        
        if not email:
            raise AuthenticationFailed("Email is required")
        
        # Find user by email and get their username
        try:
            user = User.objects.get(email=email)
            print(f"✅ [DEBUG] User found: {user.username}")
            
            # Set the username for the parent serializer to use
            attrs['username'] = user.username
            
            # Authenticate the user
            authenticated_user = authenticate(username=user.username, password=password)
            
            if authenticated_user is None:
                print(f"❌ [DEBUG] Authentication failed - invalid password")
                raise AuthenticationFailed("Invalid email or password")
            
            print(f"✅ [DEBUG] Authentication successful for: {user.username}")
            
        except User.DoesNotExist:
            print(f"❌ [DEBUG] No user found with email: {email}")
            raise AuthenticationFailed("Invalid email or password")
        
        # Call parent validate with username now included
        return super().validate(attrs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("📩 [DEBUG] Login API called")
        print(f"📧 Email received: {request.data.get('email')}")
        print(f"🔐 Password received: {'*' * len(request.data.get('password', ''))}")
        
        logger.info(f"Login attempt for: {request.data.get('email')}")
        
        try:
            response = super().post(request, *args, **kwargs)
            print("✅ [DEBUG] Authentication successful")
            logger.info(f"Login successful for: {request.data.get('email')}")
            return response
        except Exception as e:
            print(f"❌ [DEBUG] Authentication failed: {str(e)}")
            logger.error(f"Login failed for {request.data.get('email')}: {str(e)}")
            raise