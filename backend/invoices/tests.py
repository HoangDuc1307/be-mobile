from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rooms.models import Room, RoomTenant
from invoices.models import UnitPrice, Invoice

User = get_user_model()

class InvoiceAPITests(APITestCase):

    def setUp(self):
        # Tạo chủ trọ
        self.owner = User.objects.create_superuser(
            username='landlord',
            password='password123',
            phone='0987654321',
            email='landlord@example.com'
        )
        # Tạo khách thuê (đã có sẵn tài khoản)
        self.existing_tenant = User.objects.create_user(
            username='existing_tenant',
            password='password123',
            phone='0123456789',
            first_name='Nguyen Van Tenant',
            id_card='123456789'
        )
        # Tạo phòng
        self.room = Room.objects.create(
            name='Phòng 101',
            price=3000000,
            area=25.0,
            status='available',
            description='Phòng tầng 1'
        )

        # Login chủ trọ
        login_url = reverse('login')
        response = self.client.post(login_url, {'username': 'landlord', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_unit_price_get_default_and_post_update(self):
        # 1. GET - Phải tự động tạo và trả về giá trị mặc định
        url = reverse('unit-price')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['electricity_price'], '3500')
        self.assertEqual(response.data['water_price'], '15000')
        self.assertEqual(response.data['common_service_fee'], '100000')
        self.assertTrue('last_updated' in response.data)

        # 2. POST - Cập nhật giá trị mới
        data = {
            'electricity_price': 4000,
            'water_price': 18000,
            'common_service_fee': 120000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['electricity_price'], '4000')
        self.assertEqual(response.data['water_price'], '18000')
        self.assertEqual(response.data['common_service_fee'], '120000')

        # Kiểm tra database đã lưu đúng
        db_price = UnitPrice.objects.get(owner=self.owner)
        self.assertEqual(db_price.electricity_price, 4000)

    def test_assign_tenant_new_user(self):
        # Gán khách thuê mới chưa có tài khoản
        url = reverse('assign-tenant', kwargs={'room_id': self.room.id})
        data = {
            'name': 'Trần Văn B',
            'phone': '0909090909',
            'id_card': '987654321',
            'move_in': '2026-06-01',
            'deposit': 1500000,
            'duration_months': 6
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], '0909090909')
        self.assertEqual(response.data['password'], '123456')

        # Kiểm tra tài khoản User mới được tạo
        new_user = User.objects.get(phone='0909090909')
        self.assertEqual(new_user.first_name, 'Trần Văn B')
        self.assertEqual(new_user.id_card, '987654321')

        # Kiểm tra RoomTenant được tạo
        tenant_contract = RoomTenant.objects.get(room=self.room, is_active=True)
        self.assertEqual(tenant_contract.tenant, new_user)
        self.assertEqual(tenant_contract.deposit, 1500000)
        self.assertEqual(tenant_contract.duration_months, 6)
        
        # Kiểm tra trạng thái phòng đổi thành occupied
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'occupied')

    def test_assign_tenant_existing_user_by_phone(self):
        # Gán khách thuê đã có tài khoản sẵn trong hệ thống (tìm theo số điện thoại)
        url = reverse('assign-tenant', kwargs={'room_id': self.room.id})
        data = {
            'name': 'Nguyen Van Tenant Updated Name',
            'phone': '0123456789', # Trùng phone với self.existing_tenant
            'id_card': '123456789-updated',
            'move_in': '2026-06-02',
            'deposit': 2000000,
            'duration_months': 12
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'existing_tenant')
        self.assertEqual(response.data['password'], 'Sử dụng mật khẩu cũ')

        # Kiểm tra tài khoản cũ được cập nhật
        self.existing_tenant.refresh_from_db()
        self.assertEqual(self.existing_tenant.first_name, 'Nguyen Van Tenant Updated Name')
        self.assertEqual(self.existing_tenant.id_card, '123456789-updated')

        # Kiểm tra RoomTenant tạo thành công với user cũ
        tenant_contract = RoomTenant.objects.get(room=self.room, is_active=True)
        self.assertEqual(tenant_contract.tenant, self.existing_tenant)
        self.assertEqual(tenant_contract.deposit, 2000000)

    def test_assign_tenant_by_tenant_id(self):
        url = reverse('assign-tenant', kwargs={'room_id': self.room.id})
        data = {
            'tenant_id': self.existing_tenant.id,
            'name': 'Nguyen Van Tenant',
            'phone': '0123456789',
            'id_card': '123456789',
            'move_in': '2026-06-03',
            'deposit': 2500000,
            'duration_months': 12,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tenant_id'], self.existing_tenant.id)
        self.assertEqual(response.data['room_id'], self.room.id)

        tenant_contract = RoomTenant.objects.get(room=self.room, is_active=True)
        self.assertEqual(tenant_contract.tenant, self.existing_tenant)

    def test_invoice_creation_and_auto_calculation(self):
        # Thiết lập đơn giá trước
        UnitPrice.objects.create(
            owner=self.owner,
            electricity_price=4000,
            water_price=18000,
            common_service_fee=150000
        )

        url = reverse('invoice-list-create')
        data = {
            'room': self.room.id,
            'month': 6,
            'year': 2026,
            'room_price': 3000000,
            'electricity_usage': 50, # Sử dụng 50 kWh -> 50 * 4000 = 200.000
            'water_usage': 5,        # Sử dụng 5 khối -> 5 * 18000 = 90.000
            'service_price': 150000
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_electric'], '200000')
        self.assertEqual(response.data['total_water'], '90000')
        # Grand total = 3.000.000 (phòng) + 200.000 (điện) + 90.000 (nước) + 150.000 (dịch vụ) = 3.440.000
        self.assertEqual(response.data['grand_total'], '3440000')

        # Kiểm tra DB
        invoice = Invoice.objects.get(room=self.room, month=6, year=2026)
        self.assertEqual(invoice.electricity_price, 4000)
        self.assertEqual(invoice.water_price, 18000)
        self.assertEqual(invoice.grand_total, 3440000)
