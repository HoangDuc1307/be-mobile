# be-mobile

Backend API Django REST Framework cho ứng dụng quản lý phòng trọ (mobile).

Repository: [https://github.com/HoangDuc1307/be-mobile](https://github.com/HoangDuc1307/be-mobile)

## Công nghệ

- Python 3.13+
- Django 6.0
- Django REST Framework
- PostgreSQL
- JWT (SimpleJWT)
- django-cors-headers

## Cấu trúc thư mục

```
be-mobile/
├── config/          # Cấu hình Django (settings, urls, wsgi)
├── users/           # Đăng ký, đăng nhập, custom User (owner/tenant)
├── rooms/           # Quản lý phòng, gán/trả/chuyển người thuê
├── invoices/        # Hóa đơn (đang phát triển)
├── manage.py
├── requirements.txt
├── .env.example     # Mẫu biến môi trường
└── README.md
```

## Yêu cầu

- Python 3.13+
- PostgreSQL đã cài và chạy
- Database `nhatro_db` (hoặc tên trong `.env`)

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/HoangDuc1307/be-mobile.git
cd be-mobile
```

### 2. Tạo virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

### 3. Cài dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

```bash
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
```

Chỉnh sửa `.env` theo máy của bạn (SECRET_KEY, mật khẩu PostgreSQL, ...).

### 5. Tạo database PostgreSQL

```sql
CREATE DATABASE nhatro_db;
```

### 6. Chạy migration

```bash
python manage.py migrate
```

### 7. Chạy server

```bash
python manage.py runserver
```

API mặc định: `http://127.0.0.1:8000/`

## API Endpoints

### Xác thực (`/auth/`)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/auth/register/` | Đăng ký tài khoản |
| POST | `/auth/login/` | Đăng nhập, trả về JWT |

**Header cho các API cần đăng nhập:**

```
Authorization: Bearer <access_token>
```

### Phòng (`/api/rooms/`)

| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| GET | `/api/rooms/` | Owner/Tenant | Danh sách phòng |
| POST | `/api/rooms/` | Owner | Tạo phòng mới |
| GET | `/api/rooms/<id>/` | Authenticated | Chi tiết phòng |
| PUT | `/api/rooms/<id>/` | Owner | Cập nhật phòng |
| DELETE | `/api/rooms/<id>/` | Owner | Xóa phòng (khi trống) |
| POST | `/api/rooms/<id>/assign/` | Owner | Gán người thuê |
| POST | `/api/rooms/<id>/remove/` | Owner | Trả phòng |
| POST | `/api/rooms/<id>/transfer/` | Owner | Chuyển phòng |

### Vai trò người dùng

- `owner` — Chủ trọ: quản lý phòng, gán/trả/chuyển người thuê
- `tenant` — Người thuê: xem phòng đang thuê

## Ví dụ request

### Đăng ký

```http
POST /auth/register/
Content-Type: application/json

{
  "username": "chu_tro_01",
  "password": "matkhau123",
  "role": "owner",
  "phone": "0901234567"
}
```

### Đăng nhập

```http
POST /auth/login/
Content-Type: application/json

{
  "username": "chu_tro_01",
  "password": "matkhau123"
}
```

## Admin

```bash
python manage.py createsuperuser
```

Truy cập: `http://127.0.0.1:8000/admin/`

## License

MIT
