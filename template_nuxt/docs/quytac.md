# QUY TẮC NGẦM & KINH NGHIỆM DỰ ÁN CHAMSOCHD

> Tổng hợp các quy tắc, lưu ý, kinh nghiệm ngầm khi phát triển dự án.  
> Cập nhật lần cuối: 05/03/2026 (v2 — bổ sung quy tắc phòng lỗi)

---

## 1. UI / UX — Thiết kế giao diện

### 1.1 Mobile-first là ưu tiên số 1
- Người dùng chính (Trưởng nhóm) **thao tác trên điện thoại**.
- Mọi nút bấm, icon cần đủ lớn để bấm thoải mái (tối thiểu `44px × 44px`).
- Đang dùng `!w-14 !h-14` (56px) cho các action icon trong danh sách thành viên.

### 1.2 Icon & nút hành động trong list
- Các icon thao tác (phone, Zalo, copy, comment) đặt **cùng 1 dòng**, thẳng hàng.
- Không tách icon ghi chú sang dòng riêng so với icon phone/Zalo.
- Zalo: hiển thị chữ **"Zalo"** (không dùng chữ Z đơn lẻ vì không rõ nghĩa).
- SĐT và tên phải gần nhau, **không để khoảng cách lớn** giữa 2 dòng.

### 1.3 Hiển thị thông tin compact
- Khu vực "Hôm nay hãy hỏi thăm" dùng **inline text** thay vì card to chiếm chỗ.
- Format: `✨ Hôm nay hãy hỏi thăm [Tên - Pháp danh], [Tên - Pháp danh] 🔄`
- Tránh hiển thị avatar, số điện thoại, nhiều button trong khu vực gợi ý này.

### 1.4 Dialog thay vì chuyển trang
- Khi click vào item list → **mở dialog** chi tiết, không navigate sang trang mới.
- Giữ cho `index.vue` gọn: tách dialog nặng thành component riêng (`MemberDetailDialog.vue`).
- Component dialog tự load data khi `visible` chuyển thành `true`.

### 1.5 Alignment trong card list
- Dòng tên bên trái và dòng label thời gian bên phải phải `items-center` (không dùng `items-start`).
- Dùng `mt-0.5` giữa dòng tên và dòng SĐT (không cần `mt-1` hay nhiều hơn).

### 1.6 Form Thêm thành viên
- Giới tính mặc định: **`khong_xac_dinh`** (không phải `nam`)
- Sau khi lưu thành viên thành công: **reset form, ở lại trang** (không chuyển sang trang detail) để có thể thêm liên tục.
- Giữ lại `group_id` đã chọn sau khi reset form.
- Khu vực Import Danh bạ / Excel: dùng nút nhỏ outlined, **KHÔNG** dùng card to chiếm diện tích.
- **SĐT không bắt buộc**: user có thể tạo thành viên mà không cần SĐT. Backend skip check trùng SĐT khi phone = null.
- Khi member không có SĐT: hiển thị "Chưa có SĐT" italic cam ở danh sách, nút Gọi/Zalo mờ đi và show toast thông báo khi bấm.

### 1.7 DB Migration — phone nullable
- Bảng `members` cột `phone` đã đổi từ `NOT NULL` sang nullable.
- Khi deploy, cần gọi `/api/init` 1 lần để chạy migration (SQLite recreate table).

### 1.8 Dashboard Tổng quan
- **Stats cards**: 4 card 2x2. PHẢI có ý nghĩa hành động: Thành viên (+mới), Độ phủ CS (%), Follow-up hôm nay, Cần hỗ trợ. **KHÔNG** hiển thị số liệu tĩnh vô nghĩa (vd: số nhóm).
- **Độ phủ CS%** = số member active được liên hệ trong 30 ngày / tổng active. Màu: xanh≥70%, cam 40-70%, đỏ<40%.
- **Follow-up**: Chỉ đếm hôm nay + quá hạn. KHÔNG đếm follow-up tương lai.
- **Cần hỗ trợ**: Member có care note gần nhất là `need_help` hoặc `no_contact`.
- **Việc cần làm**: Follow-up + Gợi ý (featured) với nút Gọi/Zalo/Ghi chú inline.
- **Cảnh báo mất kết nối**: Top 5 member chưa bao giờ / >3 tháng chưa liên hệ.
- **Event Spotlight**: Sự kiện gần nhất kèm thanh tiến độ mời gọi.
- API `/api/stats`: phân quyền Leader chỉ thấy thống kê nhóm mình.

---

## 2. Dữ liệu & DB

### 2.1 Cấu trúc bảng care_notes
- Một bảng duy nhất lưu **cả ghi chú CSHN lẫn ghi chú sự kiện**.
- Phân biệt bằng cột `event_id`:
  - `event_id = NULL` → Chăm sóc hàng ngày (CSHN)
  - `event_id = <UUID>` → Gắn với sự kiện cụ thể
- `trang_thai_sk` chỉ có giá trị khi `event_id != NULL` (trạng thái tham dự sự kiện).
- `phan_hoi` (emoji cảm nhận) chỉ dùng trong CSHN mode.

### 2.2 Lấy ghi chú theo mode
- **CSHN mode** (`event_id` không truyền): lấy tất cả care_notes + attendance records.
- **Event mode** (`event_id` được truyền): chỉ lấy care_notes có `event_id = ?` tương ứng.
- Trạng thái hiển thị trên list = care_note **mới nhất** (dùng `MAX(thoi_gian)` subquery).

### 2.3 Random selection
- "Hôm nay hãy hỏi thăm" dùng `ORDER BY RANDOM() LIMIT 2` (SQLite thuần), không dùng seed theo ngày.
- Mỗi lần refresh = chọn ngẫu nhiên hoàn toàn trong số thành viên chưa được liên hệ hôm nay.

### 2.4 ⚠️ Xoá member = SOFT DELETE (QUAN TRỌNG)
- **KHÔNG BAO GIỜ** dùng `DELETE FROM members` để xoá thành viên.
- Luôn dùng `UPDATE members SET trang_thai = 'deleted'` — dữ liệu vẫn còn trong DB.
- Áp dụng cho **mọi trường hợp**: xoá đơn lẻ, xoá hàng loạt, xoá toàn bộ.
- **KHÔNG cần** cascade delete `care_notes` hay `event_attendance` khi soft delete member.

### 2.5 Trạng thái member — Quy tắc filter
- **Các trạng thái:** `active`, `paused`, `left`, `deleted`
- **"Loại khỏi danh sách"** gồm cả `left` VÀ `deleted` → filter: `trang_thai NOT IN ('left', 'deleted')`
- **"Đếm thành viên hoạt động":** `trang_thai IN ('active', 'paused')`
- **Mỗi khi query member trong bất kỳ API nào**, phải tự hỏi: "record `left` hoặc `deleted` có nên xuất hiện ở đây không?"
- **Check trùng SĐT** (thêm/sửa/import) phải loại trừ member `left` và `deleted`: `AND trang_thai NOT IN ('left', 'deleted')`

## 3. Auth & Org (Đạo Tràng)

### 3.1 Chuyển đạo tràng — phải full page reload
- Sau khi `switchOrg()` thành công → dùng `window.location.href = '/'`, **KHÔNG** dùng `navigateTo('/')`.
- Lý do: `navigateTo` chỉ chuyển route trong SPA, state/store cũ vẫn còn → data bị "kẹt" của org cũ.
- `window.location.href` reset hoàn toàn Vue app, đảm bảo load đúng data org mới.
- Áp dụng nhất quán cho **cả topbar org switcher lẫn sidebar menu org switcher**.

### 3.2 Hiển thị org đang dùng
- Phải hiển thị tên đạo tràng hiện tại ở **cả hai nơi**: topbar và sidebar menu.
- Sidebar menu: đặt org selector **ở đầu menu**, trước tất cả menu items.
- User thuộc 1 DTT → chỉ hiện tên, không có chevron/dropdown.
- User thuộc nhiều DTT → hiện chevron, click để mở dropdown chuyển đổi.

### 3.3 Phân quyền xem thành viên
- `admin` / `manager`: xem tất cả thành viên (toàn org).
- `leader`: chỉ xem thành viên thuộc nhóm mình và nhóm được gán hỗ trợ chéo (`support_group_ids`).
- API backend phải kiểm tra quyền trước khi trả data (không chỉ ẩn trên UI).

---

## 4. Code Architecture

### 4.1 Tách component khi trang quá dài
- Nếu một page `.vue` vượt ~400 dòng → xem xét tách phần nào ra component.
- Ưu tiên tách: dialog phức tạp, tab nội dung lớn, form sửa thông tin.
- Component con tự quản lý state và load data của nó (`watch visible`, `onMounted`).
- Giao tiếp qua `emit`: `@saved`, `@updated`, `@care`, `@update:visible`.

### 4.2 Layout file trong sidebar
- `AppMenu.vue`: toàn bộ nội dung sidebar (menu + user block + org switcher).
- `AppSidebar.vue`: chỉ là wrapper, import `AppMenu`.
- `AppTopbar.vue`: topbar ngang, có org switcher riêng.
- Logic org switcher **bị lặp ở cả 2 nơi** (topbar + menu) — cần đồng bộ khi thay đổi logic.

### 4.3 API response format
- Dùng helper `apiCreated(id, message)` khi tạo mới resource.
- Các API trả `{ data: [...] }` hoặc `{ data: {...} }`.
- Lỗi: dùng `createError({ statusCode, message })`.

### 4.4 useAuth composable
- `orgName = computed(() => user.value?.ten_to_chuc)` — tên org hiện tại.
- `fetchMyOrgs()` → trả về array `{ org_id, ten_to_chuc, slug, role, is_current }`.
- `switchOrg(orgId)` → đổi JWT token + cập nhật localStorage.

---

## 5. Stack kỹ thuật & môi trường

### 5.1 Deploy
- Cloudflare Pages: `.\deploy.ps1 -Prod`
- Dev local: `npm run dev` (port 3000)
- Database: Turso (libSQL/SQLite), edge-compatible

### 5.2 UI Framework
- **PrimeVue** components: Button, Dialog, Select, InputText, Tag, Badge, Toast, ProgressSpinner, Tabs, DataTable...
- **TailwindCSS** (Tailwind v4 + tailwindcss-primeui): utility classes với prefix `!` để override PrimeVue.
- Icon: PrimeIcons (`pi pi-...`).

### 5.3 Nuxt conventions
- Pages: `app/pages/`
- Components: `app/components/` (auto-import, prefix theo folder — `members/MemberCareDialog.vue` → `<MembersMemberCareDialog>`)
- Composables: `app/composables/` (auto-import)
- API routes: `server/api/` (Nitro)

---

## 6. Patterns thường dùng

### 6.1 Format số điện thoại cho Zalo
```js
const formatPhoneForZalo = (phone) =>
  phone?.startsWith('0') ? '84' + phone.slice(1) : phone

// Link: https://zalo.me/84xxxxxxxxx
```

### 6.2 Time ago tiếng Việt
```js
const timeAgo = (dateStr) => {
  // trả về "X giờ" / "X ngày" / "X tuần" / "X tháng"
}
```

### 6.3 Mở Care Dialog từ nhiều nơi
- Khi mở từ Detail Dialog → đóng Detail Dialog trước (`showDetailDialog = false`), rồi mới mở Care Dialog.
- Dùng `emit('care', member)` từ component con, page cha xử lý logic này.

### 6.4 Transition slide cho dropdown menu
```scss
.slide-org-enter-active, .slide-org-leave-active {
  transition: all 0.2s ease;
  max-height: 200px;
  overflow: hidden;
}
.slide-org-enter-from, .slide-org-leave-to {
  max-height: 0;
  opacity: 0;
}
```

---

## 7. Lưu ý khi code thêm tính năng

- Khi thêm chức năng mới → cập nhật `docs/dac_ta_he_thong.md` nếu có thay đổi spec.
- Khi thêm API endpoint → cập nhật `docs/api_reference.md`.
- **Không navigate bằng `navigateTo`** sau `switchOrg` — phải `window.location.href`.
- Khi tách component mới → đặt đúng folder (`app/components/<domain>/`) để auto-import đúng prefix.
- Luôn dùng `@click.stop` trên action button nằm trong card clickable để tránh event bubble.
- Dialog load data: watch `visible` prop, load khi `true`.

---

## 9. ⚠️ QUY TẮC TỔNG QUÁT PHÒNG LỖI

> Những nguyên tắc chung rút ra từ kinh nghiệm, áp dụng cho **mọi dự án** (không chỉ chamsochd).

### 9.1 Khi có Soft Delete → filter TOÀN BỘ query
- Nếu hệ thống dùng soft delete (set status thay vì DELETE FROM), thì **MỌI query SELECT, COUNT, check tồn tại** đều phải filter status.
- Đặc biệt dễ quên ở: check tồn tại trước INSERT/UPDATE, đếm member cho thống kê, check quyền.
- **Quy tắc:** Khi thêm trạng thái mới (VD: `deleted`), grep toàn bộ codebase tìm mọi chỗ query bảng đó và bổ sung filter.

### 9.2 Khi xoá parent → xoá hết child data
- Xoá sự kiện → phải xoá `care_notes` + `event_attendance` gắn event đó.
- Thứ tự: xoá child trước, parent sau.
- **Quy tắc:** Mỗi bảng có foreign key (dù không enforce bằng DB), phải liệt kê cascade delete cần thiết.

### 9.3 Check unique trên MỌI luồng ghi dữ liệu
- Nếu 1 field cần unique (VD: SĐT trong cùng org), phải check trùng ở **TẤT CẢ** nơi tạo/sửa record:
  - API tạo mới (POST)
  - API sửa (PUT) — nhớ loại trừ chính record đang sửa
  - API import hàng loạt
- **Quy tắc:** Khi thêm ràng buộc unique mới, grep mọi endpoint INSERT/UPDATE của bảng đó.

### 9.4 UI phải khớp quyền API
- Nếu API chỉ cho admin/manager, thì menu/nút trên UI cũng phải ẩn cho role thấp hơn.
- Không chỉ ẩn nút — phải guard cả route (middleware/redirect) để URL trực tiếp cũng không vào được.

### 9.5 Enum/trạng thái phải xử lý hết case
- Khi hiển thị giá trị dựa trên enum (giới tính, trạng thái), phải xử lý **mọi giá trị có thể**, kể cả `null` hoặc giá trị không mong đợi.
- Không dùng ternary 2 nhánh cho enum 3+ giá trị (VD: `=== 'nam' ? 'Nam' : 'Nữ'` — sai khi có `khong_xac_dinh`).

### 9.6 Khi thêm trạng thái/cột mới → Checklist
1. Grep tất cả query SELECT/COUNT liên quan
2. Grep tất cả query INSERT/UPDATE liên quan  
3. Grep tất cả chỗ hiển thị UI liên quan
4. Cập nhật tài liệu API + đặc tả
5. Thêm vào file rules để không quên

---

## 8. Import Danh bạ / Excel

### 8.1 Normalize SĐT
- **Giữ dấu `+` ở đầu** (mã quốc gia quốc tế).
- Loại bỏ tất cả ký tự không phải số: khoảng trắng, `-`, `.`, `(`, `)`.
- KHÔNG tự ý chuyển `+84` → `0` hay ngược lại. Lưu nguyên dạng sau khi strip ký tự lạ.

### 8.2 Batch Insert — Chia chunk 100 người/lần
- Import hàng loạt **KHÔNG dùng** `for...of` + `await db.execute()` từng dòng.
- Gom thành câu `INSERT INTO ... VALUES (...), (...), (...)`.
- **CHIA CHUNK 100 người/batch** (100 × 11 cột = 1,100 params). SQLite mặc định giới hạn 999 params.
- Nếu 1 chunk lỗi → ghi lỗi, tiếp tục chunk tiếp theo (không dừng toàn bộ).
- Giới hạn API: tối đa **2000 người/lần** gọi.

### 8.3 Kiểm tra trùng SĐT
- Check trùng **trong cùng org_id** (đạo tràng). Khác đạo tràng vẫn cho phép.
- Query 1 lần `SELECT phone FROM members WHERE org_id=? AND phone IN (...)`.
- SĐT trùng → báo cho user "SĐT đã tồn tại", **không insert**.

### 8.4 Đoán giới tính từ danh xưng
- Mặc định: `khong_xac_dinh` (không phải `nam` như trước).
- Prefix nữ: chị, cô, dì, gì, tỉ, tỷ, mẹ, mự, bà, thím, mợ, má.
- Prefix nam: anh, ông, chú, bác, thầy, qt (quý thầy), sư, đại đức, thượng tọa.

### 8.5 Contact Picker API
- Chỉ hoạt động trên **Android Chrome/Samsung Browser**.
- iOS Safari: **không hỗ trợ** → phải có fallback rõ ràng (hướng dẫn dùng Excel hoặc nhập tay).
- Phải gọi từ user gesture (click) — không gọi từ onMounted/setTimeout.

---

## 10. Test Automation (Vitest)

### 10.1 Cách chạy test
- Chạy Nuxt dev server trước: `npm run dev`
- Chạy test: `npx vitest run --reporter=verbose`
- File test: `tests/api/*.test.ts`
- Config: `vitest.config.ts`

### 10.2 Kinh nghiệm viết test API
- **SĐT phải unique**: Không dùng `Date.now()` + slice vì có thể trùng giữa các test chạy song song. Dùng `Math.random()` để tạo SĐT unique.
- **Cô lập dữ liệu test**: Dùng `registerTestOrg()` tạo org riêng cho mỗi test suite. Tránh phụ thuộc dữ liệu có sẵn trong DB.
- **Cleanup**: Luôn cleanup dữ liệu test trong `afterAll()`, nhưng wrap trong try-catch để không fail nếu cleanup lỗi.
- **Timeout**: Set timeout 30-60s cho beforeAll vì cần gọi DB remote (Turso).
- **Test case markdown**: Đặt tại `docs/tests/` để team QA dùng song song.
