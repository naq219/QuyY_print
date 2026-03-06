# TÀI LIỆU ĐẶC TẢ YÊU CẦU
## HỆ THỐNG QUẢN LÝ VÀ CHĂM SÓC THÀNH VIÊN TỔ CHỨC PHẬT GIÁO

> **Phiên bản:** 1.0  
> **Ngày tạo:** 25/02/2026  
> **Trạng thái:** Bản nháp — Chờ duyệt

---

## 1. Mục tiêu hệ thống

Xây dựng nền tảng web quản lý thông tin và lịch sử hoạt động của các thành viên tham gia tổ chức Phật giáo. Mục đích cốt lõi:

- **Cá nhân hóa** quá trình chăm sóc từng thành viên.
- **Ghi nhận nhanh** mọi tương tác chăm sóc (gọi điện, nhắn tin, thăm hỏi) ngay sau khi thực hiện.
- **Theo dõi lịch sử** chăm sóc và hoạt động theo thời gian để xây dựng sự gắn kết.
- **Khuyến khích** thành viên tiếp tục đồng hành trong các hoạt động tu tập và thiện nguyện.

---

## 2. Hồ sơ Thành viên (Member Profile)

### 2.1 Thông tin cơ bản

| Trường | Kiểu dữ liệu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Họ và tên | Text | ✅ | |
| Pháp danh | Text | | Có thể chưa có |
| Giới tính | Enum | ✅ | Nam / Nữ |
| Ngày sinh | Date | ✅ | Dùng cho nhắc sinh nhật |
| Số điện thoại chính | Text | ✅ | |
| Số điện thoại phụ | Text | | |
| Zalo / Facebook | Text | | Kênh liên lạc phổ biến |
| Tỉnh / Thành phố | Text | | Theo đơn vị hành chính mới của Việt Nam |
| Xã / Phường | Text | | Theo đơn vị hành chính mới (đã bỏ cấp huyện) |
| Địa chỉ chi tiết | Text | | Số nhà, đường, thôn/ấp... |
| Ảnh đại diện | Image | | |

### 2.2 Thông tin cá nhân & Đời sống

| Trường | Kiểu dữ liệu | Ghi chú |
|---|---|---|
| Công việc | Text | |
| Tình trạng sức khỏe | Text | Ghi chú đặc biệt (bệnh mãn tính, cần hỗ trợ...) |
| Kỹ năng đặc biệt | Text | Nấu ăn, lái xe, y tế... — hữu ích khi tổ chức sự kiện |

### 2.3 Thông tin quản lý

| Trường | Kiểu dữ liệu | Ghi chú |
|---|---|---|
| Ngày gia nhập | Date | Ngày thêm vào hệ thống |
| Người giới thiệu | Text / Liên kết | Liên kết đến thành viên khác (nếu có) |
| Nhóm tĩnh (NTT) | Liên kết | Nhóm được gán khi gia nhập |
| Trạng thái | Enum | `Đang hoạt động` / `Tạm nghỉ` / `Đã rời nhóm` |
| Ghi chú cá nhân | Text (dài) | Trưởng nhóm ghi nhận đặc điểm riêng |

---

## 3. Nhóm Tĩnh (NTT — Static Group)

### 3.1 Mô tả

- Là nhóm cố định, được gán cho thành viên khi mới thêm vào hệ thống.
- Ví dụ: nhóm theo khu vực địa lý, nhóm đạo tràng cụ thể.
- Mỗi thành viên thuộc **ít nhất một** nhóm tĩnh.
- Quản trị viên (Admin) hoặc Quản lý cấp cao có quyền tạo/xóa/sửa nhóm tĩnh.

### 3.2 Thông tin nhóm

| Trường | Kiểu dữ liệu | Ghi chú |
|---|---|---|
| Tên nhóm | Text | Ví dụ: "Đạo tràng Quận 1", "Nhóm Bình Dương" |
| Mô tả | Text | |
| Trưởng nhóm phụ trách | Liên kết User | Có thể nhiều người |
| Số lượng thành viên | Tự động đếm | |
| Ngày tạo | Date | |

---

## 4. Ghi chú Chăm sóc Nhanh (Quick Care Note) ⚡

> [!IMPORTANT]
> Đây là tính năng cốt lõi của hệ thống, thiết kế ưu tiên tốc độ thao tác.

### 4.1 Mục tiêu

Cho phép Trưởng nhóm **ghi lại ngay lập tức** sau khi gọi điện hoặc nhắn tin cho thành viên, chỉ cần vài thao tác đơn giản.

### 4.2 Luồng thao tác

```
Bước 1: Vào hồ sơ thành viên (tìm kiếm nhanh theo tên/SĐT)
Bước 2: Nhấn nút "📝 Ghi chú nhanh" (nổi bật, dễ nhấn trên mobile)
Bước 3: Chọn hình thức + Nhập nội dung
Bước 4: Nhấn "Lưu" → Xong
```

### 4.3 Cấu trúc một Care Note

| Trường | Kiểu dữ liệu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Thời gian | DateTime | ✅ | Tự động lấy thời gian hiện tại, cho phép chỉnh sửa |
| Hình thức | Enum | ✅ | `📞 Gọi điện` / `💬 Nhắn tin` / `🏠 Thăm trực tiếp` / `🎁 Gửi quà` / `📋 Khác` |
| Nội dung | Text (dài) | ✅ | Ghi nhanh nội dung cuộc trao đổi |
| Phản hồi | Enum | | `😊 Vui vẻ` / `😐 Bình thường` / `😟 Cần hỗ trợ thêm` / `📵 Không liên lạc được` |
| Cần follow-up | Boolean | | Tick nếu cần liên lạc lại |
| Ngày follow-up | Date | | Nhắc nhở liên lạc lại vào ngày này |
| Người ghi | Liên kết User | ✅ | Tự động gắn tài khoản đang đăng nhập |

### 4.4 Hiển thị lịch sử Care Note

Khi vào hồ sơ thành viên, tab **"Lịch sử chăm sóc"** hiển thị:

```
┌─────────────────────────────────────────────────┐
│  📞 Gọi điện — 24/02/2026, 15:30                │
│  Người chăm sóc: Nguyễn Văn A                   │
│  Nội dung: Hỏi thăm sức khỏe, anh B nói         │
│  dạo này bận công việc nên chưa đi chùa được.    │
│  Hẹn tham gia lại vào tháng sau.                 │
│  Phản hồi: 😊 Vui vẻ                             │
│  ⏰ Follow-up: 15/03/2026                        │
├─────────────────────────────────────────────────┤
│  💬 Nhắn tin — 10/02/2026, 09:15                 │
│  Người chăm sóc: Nguyễn Văn A                   │
│  Nội dung: Gửi lời chúc mừng sinh nhật.          │
│  Phản hồi: 😊 Vui vẻ                             │
├─────────────────────────────────────────────────┤
│  📞 Gọi điện — 15/01/2026, 14:00                │
│  Người chăm sóc: Trần Thị C                     │
│  Nội dung: Mời tham gia buổi tụng kinh ngày      │
│  20/01. Anh B đồng ý sẽ tham gia.               │
│  Phản hồi: 😊 Vui vẻ                             │
└─────────────────────────────────────────────────┘
```

- Sắp xếp theo **thời gian mới nhất lên trên**.
- Có thể **lọc** theo: hình thức, khoảng thời gian, người chăm sóc.
- Có thể **tìm kiếm** trong nội dung ghi chú.

---

## 5. Quản lý Sự kiện (Event)

### 5.1 Thông tin sự kiện

| Trường | Kiểu dữ liệu | Bắt buộc | Ghi chú |
|---|---|---|---|
| Tên sự kiện | Text | ✅ | |
| Loại hình | Enum | ✅ | `Tụng kinh` / `Thiện nguyện` / `Khóa tu` / `Lễ hội` / `Khác` |
| Thời gian bắt đầu | DateTime | ✅ | |
| Thời gian kết thúc | DateTime | | |
| Địa điểm | Text | | |
| Mô tả | Text | | |
| Trạng thái | Enum | ✅ | `Lên kế hoạch` / `Đang diễn ra` / `Đã kết thúc` / `Hủy` |

### 5.2 Điểm danh & Lịch sử hoạt động

- Khi sự kiện diễn ra, cho phép **điểm danh** thành viên tham gia (chọn từ danh sách hoặc tìm kiếm nhanh).
- Kết quả điểm danh tự động cập nhật vào **Lịch sử hoạt động** (Activity Log) trong hồ sơ thành viên.
- Trong hồ sơ thành viên, tab **"Lịch sử hoạt động"** hiển thị danh sách các sự kiện đã tham gia, kèm thời gian.

---

## 6. Phân quyền Hệ thống (Role-based Access Control)

### 6.1 Bảng phân quyền

| Chức năng | Trưởng nhóm | Quản lý cấp cao | Admin |
|---|---|---|---|
| **Xem danh sách thành viên** | Chỉ nhóm mình | Tất cả | Tất cả |
| **Xem chi tiết hồ sơ** | Chỉ nhóm mình | Tất cả | Tất cả |
| **Thêm thành viên mới** | Vào nhóm mình | Vào bất kỳ nhóm | Vào bất kỳ nhóm |
| **Sửa thông tin thành viên** | Chỉ nhóm mình | Tất cả | Tất cả |
| **Ghi Care Note** | Chỉ nhóm mình *(hoặc nhóm được giao hỗ trợ chéo)* | Tất cả | Tất cả |
| **Xem lịch sử Care Note** | Chỉ nhóm mình | Tất cả | Tất cả |
| **Tạo / Quản lý sự kiện** | ❌ | ✅ | ✅ |
| **Điểm danh sự kiện** | Chỉ nhóm mình | Tất cả | Tất cả |
| **Xem thống kê & Báo cáo** | Nhóm mình | Toàn hệ thống | Toàn hệ thống |
| **Quản lý Nhóm Tĩnh (NTT)** | ❌ | ✅ | ✅ |
| **Quản lý tài khoản người dùng** | ❌ | ❌ | ✅ |
| **Cấu hình hệ thống** | ❌ | ❌ | ✅ |
| **Hỗ trợ chéo nhóm khác** | Khi được Admin chỉ định | — | Chỉ định |

### 6.2 Ghi chú về hỗ trợ chéo

- Admin có thể gán một Trưởng nhóm hỗ trợ thêm **một hoặc nhiều NTT khác** ngoài nhóm chính.
- Khi được gán, Trưởng nhóm có toàn quyền chăm sóc nhóm hỗ trợ chéo như nhóm chính của mình.

---

## 7. Thống kê & Báo cáo

### 7.1 Dashboard tổng quan (cho Quản lý cấp cao & Admin)

| Chỉ số | Mô tả |
|---|---|
| Tổng số thành viên | Phân theo trạng thái (Hoạt động / Tạm nghỉ / Rời nhóm) |
| Thành viên mới | Số lượng gia nhập trong tháng/quý |
| Tổng lượt chăm sóc | Số Care Note được ghi trong tuần/tháng |
| Thành viên chưa được chăm sóc | Danh sách thành viên chưa có Care Note trong X ngày |
| Sinh nhật sắp tới | Danh sách thành viên có sinh nhật trong 7 ngày tới |
| Sự kiện sắp diễn ra | Lịch sự kiện |

### 7.2 Báo cáo chăm sóc theo Trưởng nhóm

| Chỉ số | Mô tả |
|---|---|
| Số lượt chăm sóc | Của từng Trưởng nhóm trong khoảng thời gian |
| Tỷ lệ chăm sóc | % thành viên đã được chăm sóc / tổng thành viên nhóm |
| Danh sách chưa chăm sóc | Thành viên trong nhóm chưa được liên lạc |
| Các follow-up quá hạn | Care Note có follow-up đã qua ngày hẹn |

### 7.3 Báo cáo sự kiện

| Chỉ số | Mô tả |
|---|---|
| Số sự kiện đã tổ chức | Theo tháng/quý |
| Tỷ lệ tham gia | Số người tham gia / tổng số thành viên |
| Thành viên tham gia nhiều nhất | Top thành viên tích cực |
| Thành viên chưa từng tham gia | Danh sách cần quan tâm |

---

## 8. Nhắc nhở Tự động

| Loại nhắc nhở | Đối tượng nhận | Mô tả |
|---|---|---|
| Sinh nhật thành viên | Trưởng nhóm phụ trách | Nhắc trước 1–3 ngày |
| Follow-up đến hạn | Trưởng nhóm đã ghi note | Khi đến ngày follow-up đã hẹn |
| Thành viên lâu không chăm sóc | Trưởng nhóm phụ trách | Khi thành viên không có Care Note quá X ngày (cấu hình được) |
| Sự kiện sắp diễn ra | Tất cả Trưởng nhóm | Nhắc trước 3–7 ngày để mời thành viên |

---

## 9. Yêu cầu Kỹ thuật

### 9.1 Nền tảng

- **Web application** responsive — ưu tiên **mobile-first** (Trưởng nhóm thường thao tác trên điện thoại).
- Tương thích tốt trên trình duyệt Chrome, Safari, Firefox.

### 9.2 Dữ liệu

- Import danh sách thành viên từ **Excel/CSV** khi khởi tạo hệ thống.
- Export báo cáo ra **Excel/PDF**.
- Backup dữ liệu định kỳ.

### 9.3 Bảo mật

- Đăng nhập bằng tài khoản/mật khẩu.
- Mã hóa dữ liệu cá nhân nhạy cảm.
- Audit log: Ghi nhận thao tác thay đổi dữ liệu quan trọng (ai, lúc nào, thay đổi gì).

### 9.4 Tích hợp (Giai đoạn sau)

- Gửi tin nhắn qua **Zalo OA** hoặc **Telegram Bot**.
- Thông báo đẩy (push notification) trên trình duyệt.

---

## 10. Phạm vi phiên bản 1.0

### ✅ Bao gồm

- Quản lý hồ sơ thành viên (CRUD)
- Nhóm Tĩnh (CRUD + gán thành viên)
- Ghi chú chăm sóc nhanh (Quick Care Note)
- Lịch sử chăm sóc theo thành viên
- Quản lý sự kiện + Điểm danh
- Lịch sử hoạt động (Activity Log)
- Phân quyền 3 cấp (Trưởng nhóm / Quản lý / Admin)
- Dashboard & Báo cáo cơ bản
- Nhắc nhở sinh nhật, follow-up
- Import thành viên từ Excel

### ❌ Chưa bao gồm (Giai đoạn sau)

- Nhóm Động (Dynamic Group) — phân loại tự động theo hành vi
- Tích hợp gửi tin nhắn Zalo/Telegram
- Cổng thông tin cho thành viên (Member self-service)
- Ứng dụng mobile native (Android/iOS)
