from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    # write_only = Android gửi lên nhưng Django không trả password về
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'password', 'email', 'phone', 'role']

    def create(self, validated_data):
        # Dùng create_user thay vì create
        # vì create_user tự động hash password, create thì không
        user = User.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            email    = validated_data.get('email', ''),
            phone    = validated_data.get('phone', ''),
            role     = validated_data['role'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Dùng để trả thông tin user về cho Android"""
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'phone', 'role']