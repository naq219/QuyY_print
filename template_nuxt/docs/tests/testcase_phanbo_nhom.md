# Test Case: Phân Bổ & Quản Lý Nhóm

> Ngày tạo: 2026-03-06  
> Tác giả: AI Assistant  
> Liên quan: `docs/guidecodegroup.md`  
> Lần chạy API test: **2026-03-06 09:32** — **20/20 PASS** ✅  
> Lần chạy Browser test: **2026-03-06 09:35** — **9/9 UI PASS** ✅

---

## 1. Tổng quan

Bộ test case này bao gồm **3 phân vùng chính**:
- **A. Backend API** — Kiểm tra logic xử lý của server
- **B. Frontend UI/UX** — Kiểm tra giao diện người dùng
- **C. Phân quyền (Security)** — Kiểm tra access control

---

## 2. Quy ước

| Ký hiệu | Ý nghĩa |
|----------|---------|
| ✅ | Pass |
| ❌ | Fail |
| ⏳ | Chưa test |
| 🔴 | Critical |
| 🟡 | Medium |
| 🟢 | Low |

---

## A. Backend API Test Cases

### A1. GET /api/members?group_id=none — Lọc thành viên chưa có nhóm

| ID | Mô tả | Input | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|-------|-------------------|--------|------------|
| TC-A01 | Lấy danh sách thành viên chưa có nhóm | `GET /api/members?group_id=none` | Trả về 200, chỉ chứa members có `group_id IS NULL` | 🔴 | ✅ |
| TC-A02 | Lấy danh sách thành viên theo nhóm cụ thể | `GET /api/members?group_id={id}` | Trả về 200, chỉ chứa members thuộc nhóm đó | 🔴 | ✅ |
| TC-A03 | Lọc kết hợp `group_id=none` + `search` | `GET /api/members?group_id=none&search=Nguyen` | Chỉ trả về members chưa có nhóm VÀ tên chứa "Nguyen" | 🟡 | ⏳ |
| TC-A04 | Phân trang khi lọc group_id=none | `GET /api/members?group_id=none&page=1&limit=10` | Trả về tối đa 10 records, kèm meta.total đúng | 🟡 | ✅ |

### A2. POST /api/members/bulk-group — Gán/Chuyển nhóm hàng loạt

| ID | Mô tả | Input | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|-------|-------------------|--------|------------|
| TC-A05 | Happy case: Gán thành viên vào nhóm | `{ member_ids: [id1, id2], group_id: "grp1" }` | 200, `{ success: true, updated: 2 }` | 🔴 | ✅ |
| TC-A06 | Gỡ thành viên khỏi nhóm (null group) | `{ member_ids: [id1], group_id: null }` | 200, thành viên có `group_id = NULL` trong DB | 🔴 | ✅ |
| TC-A07 | Validation: member_ids rỗng | `{ member_ids: [], group_id: "grp1" }` | 400, message chứa "Cần chọn ít nhất 1 thành viên" | 🔴 | ✅ |
| TC-A08 | Validation: member_ids không phải array | `{ member_ids: "abc", group_id: "grp1" }` | 400 | 🟡 | ✅ |
| TC-A09 | Validation: không truyền member_ids | `{ group_id: "grp1" }` | 400 | 🟡 | ✅ |
| TC-A10 | group_id không tồn tại | `{ member_ids: [id1], group_id: "fake-id" }` | 404, "Nhóm đích không tồn tại" | 🔴 | ✅ |
| TC-A11 | group_id thuộc org khác | `{ member_ids: [id1], group_id: "other-org-group" }` | 404 (do WHERE có filter org) | 🔴 | ⏳ |
| TC-A12 | member_ids chứa id không tồn tại | `{ member_ids: ["fake-id"], group_id: "grp1" }` | 200, `updated: 0` (không lỗi, chỉ không update) | 🟡 | ✅ |
| TC-A13 | Gán 1 người đã có nhóm sang nhóm khác | member đang ở grp1, gán sang grp2 | 200, member.group_id = grp2 | 🔴 | ✅ |

### A3. GET /api/groups — Danh sách nhóm

| ID | Mô tả | Input | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|-------|-------------------|--------|------------|
| TC-A14 | Lấy danh sách nhóm kèm member_count | `GET /api/groups` | Response chứa `data[]` với `member_count`, `active_count` | 🟢 | ✅ |
| TC-A15 | Response chứa unassigned_count | `GET /api/groups` | Response có field `unassigned_count` >= 0 | 🟢 | ✅ |

---

## B. Frontend UI/UX Test Cases (Browser Test)

> **Lưu ý**: UI thực tế khác thiết kế `guidecodegroup.md`: dùng Dialog + Section thay vì Tabs. Tính năng tương đương.

### B1. Trang /groups/assign — Phân bổ thành viên chưa có nhóm

| ID | Mô tả | Thao tác | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|----------|-------------------|--------|------------|
| TC-B01 | Mở trang hiện tổng quan nhóm | Truy cập `/groups/assign` | Tổng quan nhóm + badge count hiện đúng | 🔴 | ✅ |
| TC-B02 | Hiển thị số lượng thành viên mỗi nhóm | Xem badge | Badge hiện đúng count: "Nhóm Test 1 (2)" | 🟡 | ✅ |
| TC-B03 | Chọn checkbox nhiều người | Tick checkbox trong dialog phân bổ | "Đã chọn: X người" cập nhật đúng | 🔴 | ✅ |
| TC-B04 | Nút "Gán vào nhóm" disabled khi chưa đủ | Chưa chọn nhóm đích | Nút disabled, không thể submit | 🔴 | ✅ |
| TC-B05 | Flow hoàn chỉnh: gán nhóm | Phân bổ ngay → chọn người → chọn nhóm → Gán | Thành viên được gán, badge cập nhật | 🔴 | ✅ |

### B2. Trang /groups/assign — Chuyển nhóm

| ID | Mô tả | Thao tác | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|----------|-------------------|--------|------------|
| TC-B06 | Chọn nhóm nguồn | Chọn 1 nhóm từ dropdown | DataTable load thành viên nhóm đó | 🔴 | ✅ |
| TC-B07 | Nhóm đích loại trừ nhóm nguồn | Chọn nhóm A ở nguồn | Dropdown đích không chứa nhóm A | 🔴 | ✅ |
| TC-B08 | Flow chuyển nhóm | Chọn nguồn → tick người → chọn đích → Chuyển | Thành công, badge cập nhật | 🔴 | ✅ |
| TC-B09 | Nút disabled khi chưa đủ | Chưa chọn người hoặc chưa chọn nhóm | Validation chặn submit | 🟡 | ✅ |

---

## C. Phân quyền (Security) Test Cases

| ID | Mô tả | Điều kiện | Kết quả mong đợi | Mức độ | Trạng thái |
|----|--------|-----------|-------------------|--------|------------|
| TC-C01 | Admin truy cập trang assign | Login: role=admin | Menu hiện, trang hoạt động, API trả 200 | 🔴 | ✅ |
| TC-C02 | Manager truy cập trang assign | Login: role=manager | Menu hiện, trang hoạt động, API trả 200 | 🔴 | ⏳ |
| TC-C03 | Leader bị chặn API bulk-group | Login: role=leader, gọi POST bulk-group | API trả **403** "Bạn không có quyền" | 🔴 | ⏳ |
| TC-C04 | Không có token (chưa đăng nhập) | Gọi POST bulk-group không header Auth | API trả **401** "Chưa đăng nhập" | 🔴 | ✅ |
| TC-C05 | Token hết hạn / sai | Truyền Bearer token giả | API trả **401** | 🟡 | ✅ |
| TC-C06 | Cross-org: member thuộc org khác | Admin org A gán member của org B | updated = 0 (WHERE có filter org_id) | 🔴 | ⏳ |

---

## D. Tổng hợp

| Phân vùng | Số lượng TC | Critical | Medium | Low |
|-----------|-------------|----------|--------|-----|
| A. Backend API | 15 | 8 | 5 | 2 |
| B. Frontend UI | 9 | 6 | 2 | 1 |
| C. Security | 6 | 5 | 1 | 0 |
| **Tổng** | **30** | **19** | **8** | **3** |

---

## E. Test Automation

Code test tự động nằm tại:
- `tests/api/bulk-group.test.ts` — Test API gán/chuyển nhóm
- `tests/api/members-filter.test.ts` — Test filter group_id=none
- `tests/api/auth-permissions.test.ts` — Test phân quyền

Chạy test: `npx vitest run`
