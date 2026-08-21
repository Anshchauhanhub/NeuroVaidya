import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address', 
                  'city', 'state', 'pincode', 'company_name', 'is_verified']
        read_only_fields = ['id', 'is_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': False}
        }

    def validate_email(self, value):
        value = value.strip().lower()
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Please enter a valid email address.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", value):
            raise serializers.ValidationError("Strong password required: Include letters and numbers/symbols.")
        return value

    def validate(self, data):
        confirm = data.get('confirm_password')
        if confirm and data['password'] != confirm:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        if 'role' not in validated_data:
            validated_data['role'] = 'patient'
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
