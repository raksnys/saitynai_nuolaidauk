import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .serializers import SimpleUserSerializer, UserSerializer
from rest_framework.response import Response
from .models import User
import jwt, datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status


# Create your views here.
SECRET = os.getenv('JWT_SECRET', 'secret')

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        payload = {
            'id':user.id,
            'exp':datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'role': user.role,
            'type': 'access'
        }
        
        refresh_payload = {
            'id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'type': 'refresh'
        }

        token = jwt.encode(payload, SECRET, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, SECRET, algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.set_cookie(key='refresh_jwt', value=refresh_token, httponly=True)
        response.data = {
            'jwt': token,
            'refresh_token': refresh_token
        }

        return response
    
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_jwt')
        
        if not refresh_token:
            raise AuthenticationFailed('No refresh token provided')
        
        try:
            payload = jwt.decode(refresh_token, SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Refresh token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid refresh token')
        
        if payload.get('type') != 'refresh':
            raise AuthenticationFailed('Invalid token type')
        
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found')
        
        new_payload = {
            'id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'role': user.role,
            'type': 'access'
        }
        new_access_token = jwt.encode(new_payload, SECRET, algorithm='HS256')

        new_refresh_payload = {
            'id': user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'type': 'refresh'
        }
        new_refresh_token = jwt.encode(new_refresh_payload, SECRET, algorithm='HS256')
        
        response = Response({'message': 'Token refreshed'})
        response.set_cookie(key='jwt', value=new_access_token, httponly=True)
        response.set_cookie(key='refresh_jwt', value=new_refresh_token, httponly=True)
        response.data = {
            'jwt': new_access_token,
            'refresh_token': new_refresh_token
        }
        
        return response


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        
        user = User.objects.filter(id = payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 8:
            return Response({'error': 'New password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.delete_cookie('refresh_jwt')
        response.data = {
            'message':'success'
        }
        return response
    
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = SimpleUserSerializer(users, many=True)
        return Response(serializer.data)