# Quản Lý Phòng Trọ (Room Management App)

Dự án quản lý phòng trọ bao gồm hai phần chính: **Backend (Django API)** và **Mobile App (Android - Kotlin)**.

## Cấu trúc thư mục (Project Structure)
- **`backend/`**: Mã nguồn phía máy chủ, xây dựng bằng Django và Django REST Framework.
- **`mobile/`**: Ứng dụng di động dành cho chủ trọ, xây dựng bằng Android (Kotlin) sử dụng Retrofit để giao tiếp với API.

---

## 1. Hướng dẫn thiết lập Backend (Django API)

### Yêu cầu hệ thống
- Python 3.10+
- PostgreSQL

### Các bước cài đặt
1. Di chuyển vào thư mục backend:
   ```bash
   cd backend
   ```
2. Tạo môi trường ảo và kích hoạt:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
4. Cấu hình biến môi trường:
   - Copy file `.env.example` thành `.env`:
     ```bash
     cp .env.example .env
     ```
   - Cập nhật thông tin kết nối PostgreSQL (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, v.v.) và `SECRET_KEY` trong file `.env`.
5. Thực hiện migrations và khởi chạy server:
   ```bash
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

---

## 2. Hướng dẫn thiết lập Mobile App (Android)

### Yêu cầu hệ thống
- Android Studio Koala hoặc phiên bản mới hơn.
- JDK 17.
- Thiết bị Android vật lý hoặc giả lập chạy Android 8.0 (API 26) trở lên.

### Các bước cài đặt
1. Mở thư mục `mobile/` bằng **Android Studio**.
2. Android Studio sẽ tự động tạo file `local.properties` chứa đường dẫn đến SDK Android của bạn.
3. Cấu hình địa chỉ IP máy chủ:
   - Mở file `mobile/app/src/main/java/com/example/quanlyphongtro/network/RetrofitClient.kt`.
   - Cập nhật biến `BASE_URL` trỏ về địa chỉ IP cục bộ của máy chạy server Django (ví dụ: `http://192.168.1.X:8000/`).
4. Build và chạy ứng dụng trên thiết bị thử nghiệm.
