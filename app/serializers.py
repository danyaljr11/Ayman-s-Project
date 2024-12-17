from rest_framework import serializers
from .models import CustomUser, Request


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'password', 'user_type', 'primary_phone', 'secondary_phone']

    def validate(self, data):
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'This email is already registered.'})
        if CustomUser.objects.filter(primary_phone=data['primary_phone']).exists():
            raise serializers.ValidationError({'primary_phone': 'This phone number is already registered.'})
        return data

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            user_type=validated_data.get('user_type', 'guest'),
            primary_phone=validated_data['primary_phone'],
            secondary_phone=validated_data.get('secondary_phone'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", default="N/A", read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'type', 'status', 'description', 'notes', 'employee', 'guest', 'employee_name']
        read_only_fields = ['id', 'type', 'employee', 'guest', 'employee_name']  # Prevent updating immutable fields


