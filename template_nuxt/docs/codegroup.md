# Tính năng: Phân bổ & Quản lý Nhóm

## 1. Mục đích

Quản lý việc gán thành viên vào nhóm (Nhóm Trưởng Thành viên). Gồm 3 thao tác:

1. **Xem ai chưa có nhóm** — phát hiện thành viên bị "bỏ sót"
2. **Gán vào nhóm** — đơn lẻ hoặc hàng loạt (batch assign)
3. **Chuyển nhóm** — di chuyển thành viên từ nhóm này sang nhóm khác

---

## 2. Trang `/groups/assign`

Giao diện chính để phân bổ nhóm. Hiển thị **2 tab**:

### Tab 1: Phân bổ (Chưa có nhóm → Nhóm)

| Cột trái | Cột phải |
|---|---|
| Danh sách thành viên `group_id IS NULL` | Dropdown chọn nhóm đích |
| Tìm kiếm theo tên / SĐT | Danh sách thành viên hiện tại của nhóm đó |
| Checkbox multi-select | Nút **[Gán vào nhóm này]** |

**Luồng:**
```
Tick nhiều người → Chọn nhóm đích → [Gán] → Người biến khỏi "Chưa có nhóm"
```

### Tab 2: Chuyển nhóm

| Cột trái | Cột phải |
|---|---|
| Dropdown chọn **Nhóm nguồn** | Dropdown chọn **Nhóm đích** |
| Danh sách thành viên nhóm nguồn | Preview số lượng nhóm đích sau khi chuyển |
| Checkbox multi-select | Nút **[Chuyển sang nhóm đích]** |

---

## 3. API

### `GET /api/members`

Thêm filter mới:

| Param | Giá trị | Mô tả |
|---|---|---|
| `group_id` | `none` | Lọc thành viên chưa có nhóm (`group_id IS NULL`) |
| `group_id` | `<uuid>` | Lọc theo nhóm cụ thể |

### `POST /api/members/bulk-group`

Gán/chuyển hàng loạt:

```json
{
  "member_ids": ["id1", "id2", "id3"],
  "group_id": "uuid-nhom-dich"
}
```

**Response:**
```json
{ "success": true, "updated": 3 }
```

---

## 4. Phân quyền

| Role | Quyền |
|---|---|
| `admin` | Xem & gán tất cả thành viên vào mọi nhóm |
| `manager` | Xem & gán thành viên trong org của mình |
| `leader` | Chỉ xem thành viên nhóm mình, không gán |

---

## 5. Nguyên tắc thiết kế

- **Không tạo nhóm ảo "Chưa có nhóm"** — dùng `group_id IS NULL` để tránh làm phức tạp các chỗ khác (filter, báo cáo, chăm sóc...)
- Thành viên mới tạo mặc định `group_id = NULL` cho đến khi được phân bổ
- Nút Phân bổ nhóm chỉ hiện với `admin` và `manager` (không hiện cho `leader`)
- Menu: **Nhóm > Phân bổ nhóm** (submenu, ẩn với role `leader`)
