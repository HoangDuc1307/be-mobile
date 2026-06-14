from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
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
        return Response(UserSerializer(request.user, context={'request': request}).data)

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
        return Response(UserSerializer(user, context={'request': request}).data)


class UploadAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response({'error': 'Vui lòng chọn ảnh'}, status=400)
        request.user.avatar = avatar
        request.user.save()
        return Response(UserSerializer(request.user, context={'request': request}).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except TokenError:
            pass
        return Response({'message': 'Đăng xuất thành công'}, status=200)


class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền truy cập danh sách khách thuê'}, status=status.HTTP_403_FORBIDDEN)
        tenants = User.objects.filter(is_superuser=False, is_staff=False).order_by('first_name')
        return Response(UserSerializer(tenants, many=True).data)
