from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer
# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({
                'error': 'Sai tên đăng nhập hoặc mật khẩu.'
            }, status=400)
        
        if not user.is_active:
            return Response({
                'error': 'Tài khoản đã bị vô hiệu hóa.'
            }, status=403)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=200)


class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền truy cập danh sách khách thuê'}, status=status.HTTP_403_FORBIDDEN)
        
        # Chỉ lấy tài khoản của khách thuê thường (không phải admin/staff)
        tenants = User.objects.filter(is_superuser=False, is_staff=False).order_by('first_name')
        serializer = UserSerializer(tenants, many=True)
        return Response(serializer.data)