from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
import jwt
import os

# Keep JWT secret consistent with application settings
SECRET = os.getenv('JWT_SECRET', os.getenv('DJANGO_SECRET_KEY', 'secret'))

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = None

        # 1) Try Authorization: Bearer <token>
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if auth_header and isinstance(auth_header, str):
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        # 2) Fallback to cookie-based token
        if not token:
            token = request.COOKIES.get('jwt')
        if not token:
            return None

        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')

        try:
            user = User.objects.get(id=payload['id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        return (user, token)
