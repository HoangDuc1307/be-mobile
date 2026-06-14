from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({'error': 'Sai tên đăng nhập hoặc mật khẩu.'}, status=400)
        if not user.is_active:
            return Response({'error': 'Tài khoản đã bị vô hiệu hóa.'}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=200)


class TenantProfileView(APIView):
    """GET / PATCH current user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        allowed = ['email', 'phone', 'full_name', 'id_card', 'first_name', 'last_name']
        for field in allowed:
            if field in request.data:
                setattr(user, field, request.data[field])

        if 'password' in request.data:
            new_pw = request.data['password']
            if len(new_pw) < 6:
                return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=400)
            user.set_password(new_pw)

        user.save()
        return Response(UserSerializer(user).data)


class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền truy cập danh sách khách thuê'}, status=status.HTTP_403_FORBIDDEN)
        tenants = User.objects.filter(is_superuser=False, is_staff=False).order_by('first_name')
        return Response(UserSerializer(tenants, many=True).data)
