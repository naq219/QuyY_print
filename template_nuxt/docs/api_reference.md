# API Reference — Chăm sóc Thành viên

> Base URL: `http://localhost:3000` (Dev) | `https://huynhde.pages.dev` (Prod)
>
> Tất cả request cần header `Authorization: Bearer <token>` (trừ `/api/auth/login`, `/api/auth/register` và `/api/init`).

---

## ⛹️ Multi-Tenant (Một DB, Nhiều Đạo Tràng)

Hệ thống hỗ trợ nhiều **Đạo Tràng (DTT)** dùng chung database với rờ-level isolation theo `org_id`:

- Mọi API tự động filter `WHERE org_id = ?` theo user đang đăng nhập (lấy từ JWT)
- Dữ liệu giữa các DTT cô lập hon toàn
- `POST /api/auth/register` — Đăng ký tổ chức mới + tài khoản admin (public)
- Một email có thể thuộc nhiều DTT, login sẽ yêu cầu chọn DTT

## Chuẩn hoá Response Format

Tất cả API đều sử dụng format chuẩn sau:

| Loại Endpoint | Response Format | Mô tả |
|---|---|---|
| **List** (GET danh sách) | `{ "data": [...], "meta"?: { total, page, limit, totalPages } }` | Mảng dữ liệu + pagination (nếu có) |
| **Detail** (GET chi tiết) | `{ "data": { ... } }` | Object dữ liệu |
| **Create** (POST) | `{ "data": { "success": true, "id": "uuid", "message": "..." } }` | ID mới + message |
| **Update** (PUT) | `{ "data": { "success": true, "message": "..." } }` | Message xác nhận |
| **Delete** (DELETE) | `{ "data": { "success": true, "message": "..." } }` | Message xác nhận |

> **Ngoại lệ:** Auth endpoints (`/api/auth/login`, `/api/auth/me`) giữ format riêng vì gắn chặt với auth composable.

---

## Mục lục
1. [Xác thực (Auth)](#1-xác-thực-auth)
2. [Thành viên (Members)](#2-thành-viên-members)
3. [Nhóm (Groups)](#3-nhóm-groups)
4. [Ghi chú chăm sóc (Care Notes)](#4-ghi-chú-chăm-sóc-care-notes)
5. [Sự kiện (Events)](#5-sự-kiện-events)
6. [Điểm danh (Attendance)](#6-điểm-danh-attendance)
7. [Tài khoản (Users)](#7-tài-khoản-users)
8. [Thống kê (Stats)](#8-thống-kê-stats)
9. [Follow-up](#9-follow-up)
10. [Khởi tạo DB (Init)](#10-khởi-tạo-db-init)
11. [Phân quyền (RBAC)](#11-phân-quyền-rbac)

---

## 1. Xác thực (Auth)

### `POST /api/auth/login`
Đăng nhập, trả về JWT token.

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `email` | string | ✅ | Email tài khoản |
| `password` | string | ✅ | Mật khẩu |

**Response 200:**
```json
{
  "token": "eyJhbGci...",
  "user": {
    "id": "uuid",
    "email": "admin@chamsoc.vn",
    "ho_ten": "Admin",
    "role": "admin",
    "group_id": null,
    "support_group_ids": []
  }
}
```

**Errors:** `400` thiếu fields, `401` sai credentials.

---

### `GET /api/auth/me`
Lấy thông tin user hiện tại từ JWT token.

**Response 200:**
```json
{
  "user": { "id", "email", "ho_ten", "role", "group_id", "support_group_ids" }
}
```

**Errors:** `401` chưa đăng nhập.

---

## 2. Thành viên (Members)

### `GET /api/members`
Danh sách thành viên với tìm kiếm, lọc, phân trang.

| Query Param | Type | Default | Mô tả |
|---|---|---|---|
| `search` | string | — | Tìm theo tên, SĐT, pháp danh |
| `group_id` | string | — | Lọc theo nhóm |
| `trang_thai` | string | — | Lọc theo trạng thái (`active`, `paused`, `left`) |
| `page` | number | `1` | Trang hiện tại |
| `limit` | number | `20` | Số bản ghi / trang |

> **RBAC:** Leader chỉ thấy thành viên trong nhóm mình + nhóm hỗ trợ chéo.

**Response 200:**
```json
{
  "data": [{ "id", "ho_ten", "phap_danh", "phone", "group_name", ... }],
  "meta": {
    "total": 50,
    "page": 1,
    "limit": 20,
    "totalPages": 3
  }
}
```

---

### `GET /api/members/:id`
Chi tiết 1 thành viên.

> **RBAC:** Leader chỉ xem được thành viên thuộc nhóm mình.

**Response 200:**
```json
{
  "data": { "id", "ho_ten", "phap_danh", "gioi_tinh", "ngay_sinh", "phone", "phone2", "zalo_fb", "tinh_tp", "xa_phuong", "dia_chi", "cong_viec", "suc_khoe", "ky_nang", "nguoi_gioi_thieu", "ghi_chu", "group_id", "group_name", "trang_thai", "ngay_gia_nhap", ... }
}
```

**Errors:** `403` không thuộc nhóm, `404` không tìm thấy.

---

### `POST /api/members`
Thêm thành viên mới.

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `ho_ten` | string | ✅ | Họ và tên |
| `gioi_tinh` | string | ✅ | `nam` hoặc `nu` |
| `ngay_sinh` | string | ✅ | Format `YYYY-MM-DD` |
| `phone` | string | ✅ | SĐT chính |
| `group_id` | string | ✅ | ID nhóm |
| `phap_danh` | string | — | Pháp danh |
| `phone2` | string | — | SĐT phụ |
| `zalo_fb` | string | — | Zalo/Facebook |
| `tinh_tp` | string | — | Tỉnh/TP |
| `xa_phuong` | string | — | Xã/Phường |
| `dia_chi` | string | — | Địa chỉ |
| `cong_viec` | string | — | Công việc |
| `suc_khoe` | string | — | Tình trạng sức khỏe |
| `ky_nang` | string | — | Kỹ năng |
| `nguoi_gioi_thieu` | string | — | Người giới thiệu |
| `ghi_chu` | string | — | Ghi chú |
| `ngay_gia_nhap` | string | — | Ngày gia nhập |

> **RBAC:** Leader chỉ thêm vào nhóm mình.

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Thêm thành viên thành công" } }`

---

### `PUT /api/members/:id`
Cập nhật thông tin thành viên. Body giống `POST`, tất cả fields optional.

> **RBAC:** Leader chỉ sửa thành viên thuộc nhóm mình.

**Response 200:** `{ "data": { "success": true, "message": "Cập nhật thành viên thành công" } }`

---

### `DELETE /api/members/:id`
Xóa mềm (soft delete) — chuyển `trang_thai` thành `left`.

> **RBAC:** Leader chỉ xóa thành viên thuộc nhóm mình.

**Response 200:** `{ "data": { "success": true, "message": "..." } }`

---

### `POST /api/members/bulk-delete`
**Soft delete** hàng loạt — chuyển `trang_thai` thành `'deleted'` cho nhiều thành viên cùng lúc. Dữ liệu vẫn còn trong DB, chỉ bị ẩn khỏi danh sách (giống cơ chế `DELETE /api/members/:id`).

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `ids` | string[] | ✅ | Mảng ID thành viên cần xóa |

> **RBAC:** Chỉ **Manager/Admin** được phép xóa hàng loạt.

**Response 200:** `{ "success": true, "updated": 10 }`

---

### `POST /api/members/delete-all`
**Soft delete** toàn bộ danh bạ của đạo tràng hiện tại — chuyển `trang_thai` thành `'deleted'` cho tất cả members chưa bị deleted.

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `confirm_text` | string | ✅ | Bắt buộc phải là `"XOA"` để xác nhận |

> **RBAC:** Chỉ **Manager/Admin** được phép thực hiện chức năng nguy hiểm này.

**Response 200:** `{ "success": true, "updated": 100 }`
---

## 3. Nhóm (Groups)

### `GET /api/groups`
Danh sách tất cả nhóm + số lượng thành viên hoạt động.

**Response 200:**
```json
{
  "data": [{ "id", "ten_nhom", "mo_ta", "member_count", "created_at" }]
}
```

---

### `POST /api/groups`
Tạo nhóm mới. **Quyền: Admin, Manager.**

| Field | Type | Required |
|---|---|:---:|
| `ten_nhom` | string | ✅ |
| `mo_ta` | string | — |

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Tạo nhóm thành công" } }`

---

### `PUT /api/groups/:id`
Cập nhật nhóm. **Quyền: Admin, Manager.**

| Field | Type | Required |
|---|---|:---:|
| `ten_nhom` | string | ✅ |
| `mo_ta` | string | — |

**Response 200:** `{ "data": { "success": true, "message": "Cập nhật nhóm thành công" } }`

**Errors:** `404` nhóm không tồn tại.

---

### `DELETE /api/groups/:id`
Xóa nhóm. **Quyền: Admin only.**

> Không thể xóa nếu nhóm còn thành viên hoạt động.

**Response 200:** `{ "data": { "success": true, "message": "Xóa nhóm thành công" } }`

**Errors:** `400` nhóm còn thành viên.

---

## 4. Ghi chú chăm sóc (Care Notes)

### `GET /api/care-notes`
Lấy ghi chú chăm sóc theo thành viên.

| Query Param | Type | Required | Mô tả |
|---|---|:---:|---|
| `member_id` | string | ✅ | ID thành viên |
| `hinh_thuc` | string | — | Lọc: `call`, `message`, `visit`, `gift`, `other` |
| `search` | string | — | Tìm trong nội dung |

> **RBAC:** Leader chỉ xem care notes của thành viên thuộc nhóm mình.

**Response 200:**
```json
{
  "data": [{
    "id", "member_id", "thoi_gian", "hinh_thuc", "noi_dung",
    "phan_hoi", "follow_up", "follow_up_date",
    "created_by", "created_by_name"
  }]
}
```

---

### `POST /api/care-notes`
Tạo ghi chú chăm sóc mới.

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `member_id` | string | ✅ | ID thành viên |
| `hinh_thuc` | string | ✅ | `call`, `message`, `visit`, `gift`, `other` |
| `noi_dung` | string | ✅ | Nội dung ghi chú |
| `thoi_gian` | string | — | ISO datetime (mặc định: hiện tại) |
| `phan_hoi` | string | — | `happy`, `normal`, `need_help`, `no_contact` |
| `follow_up` | boolean | — | Cần follow-up không |
| `follow_up_date` | string | — | Ngày follow-up `YYYY-MM-DD` |

> **RBAC:** Leader chỉ tạo cho thành viên thuộc nhóm mình.

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Ghi chú chăm sóc đã được lưu" } }`

---

### `DELETE /api/care-notes/:id`
Xóa ghi chú. Chỉ người tạo hoặc admin mới được xóa. Sử dụng `requireAuth` thay `getUserFromEvent`.

**Response 200:** `{ "data": { "success": true, "message": "Xóa ghi chú thành công" } }`

---

## 5. Sự kiện (Events)

### `GET /api/events`
Danh sách sự kiện + số người đã điểm danh.

| Query Param | Type | Mô tả |
|---|---|---|
| `trang_thai` | string | `planned`, `ongoing`, `completed`, `cancelled` |
| `search` | string | Tìm theo tên, địa điểm |

**Response 200:**
```json
{
  "data": [{
    "id", "ten_su_kien", "loai_hinh", "thoi_gian_bat_dau",
    "thoi_gian_ket_thuc", "dia_diem", "mo_ta", "trang_thai",
    "attendee_count"
  }]
}
```

---

### `GET /api/events/:id`
Chi tiết sự kiện + danh sách người đã điểm danh.

**Response 200:**
```json
{
  "data": {
    "id", "ten_su_kien", "loai_hinh", ...,
    "attendees": [{
      "id", "member_id", "ho_ten", "phap_danh", "phone",
      "group_name", "checked_in_at", "checked_in_by_name"
    }]
  }
}
```

---

### `POST /api/events`
Tạo sự kiện mới. **Quyền: Admin, Manager.**

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `ten_su_kien` | string | ✅ | Tên sự kiện |
| `loai_hinh` | string | ✅ | `tung_kinh`, `thien_nguyen`, `khoa_tu`, `le_hoi`, `khac` |
| `thoi_gian_bat_dau` | string | ✅ | ISO datetime |
| `thoi_gian_ket_thuc` | string | — | ISO datetime |
| `dia_diem` | string | — | Địa điểm |
| `mo_ta` | string | — | Mô tả |

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Tạo sự kiện thành công" } }`

---

### `PUT /api/events/:id`
Cập nhật sự kiện. **Quyền: Admin, Manager.** Body giống `POST` + thêm `trang_thai`.

**Response 200:** `{ "data": { "success": true, "message": "Cập nhật sự kiện thành công" } }`

---

### `DELETE /api/events/:id`
Xóa sự kiện + toàn bộ dữ liệu điểm danh. **Quyền: Admin only.**

**Response 200:** `{ "data": { "success": true, "message": "Xóa sự kiện thành công" } }`

---

## 6. Điểm danh (Attendance)

### `POST /api/attendance`
Điểm danh thành viên cho sự kiện.

| Field | Type | Required |
|---|---|:---:|
| `event_id` | string | ✅ |
| `member_id` | string | ✅ |

> **RBAC:** Leader chỉ điểm danh thành viên thuộc nhóm mình.
>
> Không cho phép điểm danh trùng.

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Điểm danh thành công" } }`

**Errors:** `400` đã điểm danh, `404` sự kiện/thành viên không tồn tại, `403` không thuộc nhóm.

---

### `DELETE /api/attendance/:id`
Hủy điểm danh. Chỉ người đã điểm danh hoặc admin mới được hủy.

**Response 200:** `{ "data": { "success": true, "message": "Hủy điểm danh thành công" } }`

---

### `GET /api/attendance/member/:id`
Lịch sử tham gia sự kiện (Activity Log) của 1 thành viên.

> **RBAC:** Leader chỉ xem thành viên thuộc nhóm mình.

**Response 200:**
```json
{
  "data": [{
    "checked_in_at", "ten_su_kien", "loai_hinh",
    "thoi_gian_bat_dau", "dia_diem", "checked_in_by_name"
  }]
}
```

---

## 7. Tài khoản (Users)

> **Tất cả endpoints trong nhóm này yêu cầu quyền Admin.**

### `GET /api/users`
Danh sách tài khoản + tên nhóm.

**Response 200:**
```json
{
  "data": [{
    "id", "email", "ho_ten", "role", "group_id", "group_name",
    "support_group_ids": [], "created_at"
  }]
}
```

---

### `POST /api/users`
Tạo tài khoản mới.

| Field | Type | Required | Mô tả |
|---|---|:---:|---|
| `email` | string | ✅ | Email (unique) |
| `password` | string | ✅ | Mật khẩu |
| `ho_ten` | string | ✅ | Họ và tên |
| `role` | string | ✅ | `admin`, `manager`, `leader` |
| `group_id` | string | ✅* | Bắt buộc nếu role = `leader` |
| `support_group_ids` | string[] | — | Danh sách nhóm hỗ trợ chéo (cho leader) |

**Response 200:** `{ "data": { "success": true, "id": "uuid", "message": "Tạo tài khoản thành công" } }`

**Errors:** `400` email đã tồn tại, thiếu fields, role không hợp lệ.

---

### `PUT /api/users/:id`
Cập nhật tài khoản. Body giống `POST`, `password` optional (bỏ trống = giữ nguyên).

**Response 200:** `{ "data": { "success": true, "message": "Cập nhật tài khoản thành công" } }`

---

### `DELETE /api/users/:id`
Xóa tài khoản. Admin không thể tự xóa chính mình.

**Response 200:** `{ "data": { "success": true, "message": "Xóa tài khoản thành công" } }`

---

## 8. Thống kê (Stats)

### `GET /api/stats`
Dashboard tổng quan.

**Response 200:**
```json
{
  "data": {
    "stats": {
      "totalMembers": 50,
      "totalGroups": 5,
      "careThisMonth": 12,
      "pendingFollowUp": 3
    },
    "recentNotes": [{ ... }],
    "recentMembers": [{ ... }],
    "upcomingEvents": [{ ... }],
    "upcomingBirthdays": [{
      "id", "ho_ten", "phap_danh", "phone", "ngay_sinh",
      "group_name", "days_until", "birthday_date"
    }]
  }
}
```

- `upcomingEvents`: 5 sự kiện sắp tới (planned/ongoing)
- `upcomingBirthdays`: Thành viên có sinh nhật trong **7 ngày tới**

---

## 9. Follow-up

### `GET /api/follow-ups`
Danh sách care notes cần follow-up.

> **RBAC:** Leader chỉ thấy follow-up của thành viên thuộc nhóm mình.
>
> **Sắp xếp:** Quá hạn lên đầu → theo ngày → theo thời gian gần nhất.

**Response 200:**
```json
{
  "data": [{
    "id", "member_id", "hinh_thuc", "noi_dung", "phan_hoi",
    "follow_up_date", "thoi_gian",
    "ho_ten", "phap_danh", "phone", "group_name",
    "created_by_name"
  }]
}
```

---

## 10. Khởi tạo DB (Init)

### `POST /api/init?secret=xxx`
Khởi tạo database (tạo bảng + tài khoản admin mặc định).

| Query Param | Type | Required | Mô tả |
|---|---|:---:|---|
| `secret` | string | ✅ | Phải khớp với biến `NUXT_INIT_SECRET` |

> ⚠️ **Chỉ chạy 1 lần** khi deploy lần đầu.

---

## 11. Phân quyền (RBAC)

### Ma trận quyền

| Hành động | 👤 Leader | 📊 Manager | 👑 Admin |
|---|:---:|:---:|:---:|
| Xem thành viên | Nhóm mình | ✅ Tất cả | ✅ Tất cả |
| Thêm/Sửa/Xóa thành viên | Nhóm mình | ✅ | ✅ |
| Xem/Tạo care notes | Nhóm mình | ✅ | ✅ |
| Điểm danh | Nhóm mình | ✅ | ✅ |
| Quản lý nhóm | ❌ | ✅ | ✅ |
| Tạo/Sửa sự kiện | ❌ | ✅ | ✅ |
| Xóa sự kiện | ❌ | ❌ | ✅ |
| Quản lý tài khoản | ❌ | ❌ | ✅ |

### Cơ chế "Nhóm hỗ trợ chéo"

Leader có thể được admin gán thêm `support_group_ids` — cho phép truy cập thành viên ở các nhóm khác ngoài nhóm chính (`group_id`).

### HTTP Status Codes

| Code | Ý nghĩa |
|---|---|
| `200` | Thành công |
| `400` | Dữ liệu không hợp lệ / thiếu fields |
| `401` | Chưa đăng nhập (thiếu hoặc sai token) |
| `403` | Không đủ quyền |
| `404` | Không tìm thấy resource |

### Authentication Header

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token chứa: `userId`, `email`, `role`, `groupId`, `supportGroupIds`.

### Response Helpers (server/utils/response.ts)

| Helper | Format | Dùng cho |
|---|---|---|
| `apiList(data, meta?)` | `{ data: T[], meta?: {...} }` | GET danh sách |
| `apiDetail(data)` | `{ data: T }` | GET chi tiết |
| `apiCreated(id, msg)` | `{ data: { success, id, message } }` | POST tạo mới |
| `apiUpdated(msg)` | `{ data: { success, message } }` | PUT cập nhật |
| `apiDeleted(msg)` | `{ data: { success, message } }` | DELETE xóa |
