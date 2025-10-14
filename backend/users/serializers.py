from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        return User.objects.create_user(password=password, **validated_data)
        # instance = self.Meta.model(**validated_data)
        # if password is not None:
        #     instance.set_password(password)
        # instance.save()
        # return instance
        
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    jwt = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()