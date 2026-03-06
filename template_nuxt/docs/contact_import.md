# Chức năng: Thêm thành viên từ Danh bạ Điện thoại

## Tổng quan
Cho phép người dùng mở danh bạ điện thoại, chọn nhiều liên lạc cùng lúc, rồi import hàng loạt vào hệ thống.

**Sử dụng:** Contact Picker API (Web API chuẩn W3C)

---

## Hỗ trợ nền tảng

| Nền tảng | Hỗ trợ | Ghi chú |
|---|---|---|
| Android Chrome 80+ | ✅ | Đầy đủ tính năng |
| Samsung Browser 11+ | ✅ | Đầy đủ tính năng |
| iOS Safari | ❌ | Apple không cho phép. Hiện fallback: nhập tay hoặc dùng Import Excel |
| Desktop (Win/Mac) | ❌ | Fallback: nhập tay hoặc Import Excel |

---

## Luồng xử lý

### Frontend (`ContactImportDialog.vue`)
1. Kiểm tra nền tảng → hiển thị UI phù hợp (nút "Mở danh bạ" hoặc fallback iOS)
2. Gọi `navigator.contacts.select(['name', 'tel'], { multiple: true })`
3. Normalize SĐT: loại bỏ ký tự đặc biệt, **giữ dấu `+` đầu** (mã quốc gia)
4. **Đoán giới tính** từ danh xưng trong tên (chị → nữ, anh → nam, mặc định → không xác định)
5. **Lọc trùng SĐT** trong batch (ngay trên frontend)
6. Hiển thị danh sách, cho phép sửa inline, xóa từng dòng
7. Submit tới API `/api/members/import`

### Backend (`server/api/members/import.post.ts`)
1. Validate: ho_ten, phone bắt buộc
2. Lọc trùng SĐT **trong chính batch gửi lên**
3. **Query DB 1 lần** để kiểm tra SĐT đã tồn tại trong **cùng đạo tràng** (org_id)
4. **Batch INSERT** tất cả thành viên hợp lệ trong 1 câu lệnh SQL duy nhất
5. Trả về kết quả: `{ imported, failed, errors[] }`

---

## Quy tắc xử lý SĐT

### Normalize (Frontend)
- Giữ dấu `+` ở đầu (nếu có)
- Loại bỏ: khoảng trắng, dấu `-`, `.`, `(`, `)`, và mọi ký tự không phải số
- Ví dụ: `+84 912-345.678` → `+84912345678`
- Ví dụ: `0912 345 678` → `0912345678`

### Kiểm tra trùng (Backend)
- So khớp **chính xác chuỗi phone** đã normalize
- Scope: **cùng org_id** (đạo tràng). Khác đạo tràng vẫn cho phép trùng SĐT
- SĐT trùng → báo lỗi "SĐT đã tồn tại trong đạo tràng", **không INSERT**

---

## Đoán giới tính từ tên

| Từ khóa đầu tên | Giới tính |
|---|---|
| anh, ông, chú, bác, thầy, qt, quý thầy, sư, đại đức, thượng tọa | Nam |
| chị, cô, dì, gì, tỉ, tỷ, mẹ, mự, bà, thím, mợ, má | Nữ |
| (không có từ khóa) | Không xác định |

---

## File liên quan
- `app/components/members/ContactImportDialog.vue` — Dialog chọn danh bạ
- `app/pages/members/create.vue` — Trang thêm thành viên (tích hợp dialog)
- `server/api/members/import.post.ts` — API import hàng loạt
