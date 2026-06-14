from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    # write_only = Android gửi lên nhưng Django không trả password về
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'password', 'email', 'phone', 'full_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            password = validated_data['password'],
            email    = validated_data.get('email', ''),
            phone    = validated_data.get('phone', ''),
            full_name = validated_data.get('full_name', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Dùng để trả thông tin user về cho Android"""
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'phone', 'full_name', 'id_card', 'is_owner']

    def get_is_owner(self, obj):
        return obj.is_owner()