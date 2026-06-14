# -*- coding: utf-8 -*-
"""
Chay bang lenh:
    python manage.py shell < test_data.py

Script tao du lieu mau cho ung dung quan ly phong tro.
"""

import sys
import io
# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rooms.models import Room, RoomTenant
from invoices.models import Invoice, UnitPrice, BankInfo
from notifications.models import Notification
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

print("=== Xóa dữ liệu cũ ===")
Notification.objects.all().delete()
Invoice.objects.all().delete()
RoomTenant.objects.all().delete()
Room.objects.all().delete()
BankInfo.objects.all().delete()
UnitPrice.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# ── 1. Tạo tài khoản admin/chủ trọ ───────────────────────────────────────────
print("=== Tạo tài khoản Admin ===")
admin, _ = User.objects.get_or_create(username='admin')
admin.email       = 'admin@nhatro.vn'
admin.full_name   = 'Nguyễn Thị Lan'
admin.phone       = '0901234567'
admin.is_staff    = True
admin.is_superuser = True
admin.set_password('admin123')
admin.save()
print(f"  Admin: {admin.username} / admin123")

# ── 2. Đơn giá ───────────────────────────────────────────────────────────────
print("=== Tạo đơn giá ===")
unit_price, _ = UnitPrice.objects.get_or_create(
    owner=admin,
    defaults={
        'electricity_price':  3500,
        'water_price':        15000,
        'common_service_fee': 100000,
    }
)

# ── 3. Thông tin tài khoản ngân hàng ─────────────────────────────────────────
print("=== Tạo thông tin ngân hàng ===")
bank = BankInfo.objects.create(
    bank_name      = 'Vietcombank',
    account_number = '1234567890',
    account_name   = 'NGUYEN THI LAN',
    is_active      = True,
)

# ── 4. Tạo các phòng ─────────────────────────────────────────────────────────
print("=== Tạo phòng ===")
rooms_data = [
    {
        'name': 'Phòng 101', 'price': 3000000, 'area': 20.0, 'status': 'occupied',
        'floor': 'Tầng 1', 'capacity': 2,
        'amenities': 'Wifi, Nhà vệ sinh riêng',
        'description': 'Phòng tầng 1, yên tĩnh, đầy đủ nội thất cơ bản. Sức chứa 2 người.',
    },
    {
        'name': 'Phòng 201', 'price': 3500000, 'area': 25.0, 'status': 'occupied',
        'floor': 'Tầng 2', 'capacity': 2,
        'amenities': 'Wifi, Điều hòa, Nhà vệ sinh riêng',
        'description': 'Phòng tầng 2 có điều hòa, ban công nhỏ. Sức chứa 2 người.',
    },
    {
        'name': 'Phòng 302', 'price': 3800000, 'area': 28.0, 'status': 'available',
        'floor': 'Tầng 3', 'capacity': 3,
        'amenities': 'Wifi, Điều hòa, Máy giặt, Có gác',
        'description': 'Phòng tầng 3 rộng rãi, có gác lửng, điều hòa và máy giặt. Sức chứa 3 người.',
    },
    {
        'name': 'Phòng 303', 'price': 3600000, 'area': 26.0, 'status': 'available',
        'floor': 'Tầng 3', 'capacity': 2,
        'amenities': 'Wifi, Điều hòa, Ban công',
        'description': 'Phòng tầng 3, hướng Đông, ban công thoáng mát. Sức chứa 2 người.',
    },
    {
        'name': 'Phòng 401', 'price': 4200000, 'area': 32.0, 'status': 'available',
        'floor': 'Tầng 4', 'capacity': 4,
        'amenities': 'Wifi, Điều hòa, Máy giặt, Bếp riêng, Ban công',
        'description': 'Phòng tầng 4 cao cấp, view đẹp, đầy đủ tiện nghi. Sức chứa 4 người.',
    },
    {
        'name': 'Phòng 402', 'price': 3200000, 'area': 22.0, 'status': 'occupied',
        'floor': 'Tầng 4', 'capacity': 2,
        'amenities': 'Wifi, Nhà vệ sinh riêng',
        'description': 'Phòng tầng 4 giá bình dân, view thoáng. Sức chứa 2 người.',
    },
]

room_objs = {}
for rd in rooms_data:
    r = Room.objects.create(**rd)
    room_objs[r.name] = r
    print(f"  Phòng: {r.name} ({r.status})")

# ── 5. Tạo khách thuê ─────────────────────────────────────────────────────────
print("=== Tạo khách thuê ===")
tenants_data = [
    {
        'username': '0912345678', 'password': '123456',
        'full_name': 'Trần Văn Bình', 'phone': '0912345678',
        'email': 'binh.tran@gmail.com', 'id_card': '001099012345',
    },
    {
        'username': '0987654321', 'password': '123456',
        'full_name': 'Lê Thị Hương', 'phone': '0987654321',
        'email': 'huong.le@gmail.com', 'id_card': '001099054321',
    },
    {
        'username': '0966778899', 'password': '123456',
        'full_name': 'Phạm Minh Tuấn', 'phone': '0966778899',
        'email': 'tuan.pham@gmail.com', 'id_card': '001099078901',
    },
]

tenant_objs = {}
for td in tenants_data:
    pw = td.pop('password')
    t  = User.objects.create_user(password=pw, **td)
    tenant_objs[t.username] = t
    print(f"  Tenant: {t.username} ({t.full_name}) / {pw}")

t1 = tenant_objs['0912345678']
t2 = tenant_objs['0987654321']
t3 = tenant_objs['0966778899']

# ── 6. Gán phòng cho khách thuê ──────────────────────────────────────────────
print("=== Gán phòng ===")
r101 = room_objs['Phòng 101']
r201 = room_objs['Phòng 201']
r402 = room_objs['Phòng 402']

rt1 = RoomTenant.objects.create(
    room=r101, tenant=t1,
    move_in=date(2024, 1, 1), deposit=3000000, duration_months=12, is_active=True
)
rt2 = RoomTenant.objects.create(
    room=r201, tenant=t2,
    move_in=date(2024, 3, 1), deposit=3500000, duration_months=6, is_active=True
)
rt3 = RoomTenant.objects.create(
    room=r402, tenant=t3,
    move_in=date(2024, 6, 1), deposit=3200000, duration_months=12, is_active=True
)
print(f"  {t1.full_name} → {r101.name}")
print(f"  {t2.full_name} → {r201.name}")
print(f"  {t3.full_name} → {r402.name}")

# ── 7. Tạo hóa đơn ───────────────────────────────────────────────────────────
print("=== Tạo hóa đơn ===")

def make_invoice(room, month, year, elec, water, is_paid=False):
    room_price    = room.price
    total_electric = elec * unit_price.electricity_price
    total_water    = water * unit_price.water_price
    service_price  = unit_price.common_service_fee
    grand_total    = int(room_price) + int(total_electric) + int(total_water) + int(service_price)
    inv = Invoice.objects.create(
        room=room, month=month, year=year,
        room_price=room_price,
        electricity_usage=elec, water_usage=water,
        service_price=service_price,
        electricity_price=unit_price.electricity_price,
        water_price=unit_price.water_price,
        total_electric=total_electric,
        total_water=total_water,
        grand_total=grand_total,
        is_paid=is_paid,
    )
    status = '✓ Đã TT' if is_paid else '✗ Chưa TT'
    print(f"  {room.name} {month}/{year}: {grand_total:,}đ  {status}")
    return inv

# Phòng 101 - t1: tháng 4,5 đã trả; tháng 6 chưa trả
inv101_4 = make_invoice(r101, 4, 2024, elec=150, water=8, is_paid=True)
inv101_5 = make_invoice(r101, 5, 2024, elec=160, water=9, is_paid=True)
inv101_6 = make_invoice(r101, 6, 2024, elec=200, water=10, is_paid=False)

# Phòng 201 - t2
inv201_4 = make_invoice(r201, 4, 2024, elec=180, water=10, is_paid=True)
inv201_5 = make_invoice(r201, 5, 2024, elec=170, water=9,  is_paid=True)
inv201_6 = make_invoice(r201, 6, 2024, elec=210, water=11, is_paid=False)

# Phòng 402 - t3
inv402_6 = make_invoice(r402, 6, 2024, elec=130, water=7, is_paid=False)

# ── 8. Tạo thông báo ─────────────────────────────────────────────────────────
print("=== Tạo thông báo ===")

notifications = [
    # Tenant 1
    Notification(
        tenant=t1, notif_type='payment_due', is_read=False,
        invoice_id=inv101_6.id,
        title='Đến hạn thanh toán tháng 6',
        body=f'{r101.name} chưa thanh toán hóa đơn tháng 6/2024. Vui lòng thanh toán trước ngày 05/07/2024.',
    ),
    Notification(
        tenant=t1, notif_type='payment_success', is_read=False,
        invoice_id=inv101_5.id,
        title='Thanh toán thành công tháng 5',
        body=f'{r101.name} đã nhận thanh toán {int(inv101_5.grand_total):,}đ tháng 5/2024. Cảm ơn bạn!',
    ),
    Notification(
        tenant=t1, notif_type='system', is_read=True,
        title='Bảo trì hệ thống',
        body='Hệ thống sẽ bảo trì vào 02:00–04:00 ngày 10/07/2024. Xin lỗi vì sự bất tiện.',
    ),
    Notification(
        tenant=t1, notif_type='contract', is_read=True,
        title='Hợp đồng sắp hết hạn',
        body=f'Hợp đồng thuê {r101.name} sẽ hết hạn vào ngày 01/01/2025. Vui lòng liên hệ chủ nhà để gia hạn.',
    ),
    # Tenant 2
    Notification(
        tenant=t2, notif_type='payment_due', is_read=False,
        invoice_id=inv201_6.id,
        title='Đến hạn thanh toán tháng 6',
        body=f'{r201.name} chưa thanh toán hóa đơn tháng 6/2024. Số tiền: {int(inv201_6.grand_total):,}đ.',
    ),
    Notification(
        tenant=t2, notif_type='payment_success', is_read=True,
        invoice_id=inv201_5.id,
        title='Thanh toán thành công tháng 5',
        body=f'{r201.name} đã nhận {int(inv201_5.grand_total):,}đ tháng 5/2024.',
    ),
    # Tenant 3
    Notification(
        tenant=t3, notif_type='new_invoice', is_read=False,
        invoice_id=inv402_6.id,
        title='Hóa đơn tháng 6 đã sẵn sàng',
        body=f'{r402.name}: Hóa đơn tháng 6/2024 là {int(inv402_6.grand_total):,}đ. Hạn thanh toán: 05/07/2024.',
    ),
]
Notification.objects.bulk_create(notifications)
print(f"  Đã tạo {len(notifications)} thông báo")

print()
print("=" * 55)
print("✅  DỮ LIỆU MẪU ĐÃ TẠO THÀNH CÔNG!")
print("=" * 55)
print()
print("TÀI KHOẢN ĐĂNG NHẬP:")
print(f"  Admin   : admin / admin123")
print(f"  Tenant 1: {t1.username} / 123456  ({t1.full_name} – {r101.name})")
print(f"  Tenant 2: {t2.username} / 123456  ({t2.full_name} – {r201.name})")
print(f"  Tenant 3: {t3.username} / 123456  ({t3.full_name} – {r402.name})")
print()
print("NGÂN HÀNG:")
print(f"  {bank.bank_name} – STK: {bank.account_number} – {bank.account_name}")
print()
print("ENDPOINT CẦN CHẠY SAU KHI TẠO DỮ LIỆU:")
print("  GET  /api/rooms/available/       – Danh sách phòng trống")
print("  GET  /api/rooms/tenant-room/     – Dashboard khách thuê")
print("  GET  /api/rooms/tenant-contract/ – Hợp đồng")
print("  GET  /api/invoices/current-unpaid/ – Hóa đơn chưa thanh toán")
print("  GET  /api/notifications/         – Thông báo")
print("  GET  /auth/profile/              – Hồ sơ cá nhân")
