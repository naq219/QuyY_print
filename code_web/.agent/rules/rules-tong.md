---
trigger: always_on
---

- luôn lưu lại rules, hướng dẫn để tránh gặp lại lỗi code, hoặc khi tôi có yêu cầu rule nào mới
- luôn cập nhật lại tài liệu đặc tả hoặc tài liệu liên quan khi có thay đổi
- luôn lưu quy tắc ngầm vào rules quytacng

## Lưu ý kỹ thuật
- Vue SFC chỉ cho phép **1 block `<script setup>`** duy nhất. Không được có 2 block script setup trong cùng 1 file .vue
- Static files (ảnh, font) phải đặt trong thư mục `public/` để truy cập được từ URL
- Port dev server có thể bị chiếm bởi project khác → kiểm tra port thực tế (3001, 3002...)
- Port từ Python sang JS: `int()` → `Math.trunc()` (KHÔNG phải `Math.floor()` vì behavior khác với số âm)
- Import `xlsx` phải dùng dynamic import `await import('xlsx')` trong Nuxt (tránh SSR error)
- PowerShell: `&&` không hoạt động → tách thành 2 lệnh riêng hoặc dùng `;`
- `useConfigManager` dùng `import.meta.server` guard khi truy cập localStorage (SSR safe)
- Font VNI: phải load bằng FontFace API cho canvas, đồng thời embed vào pdf-lib cho PDF
- Composable dùng `useState()` thay `ref()` khi cần share state giữa các component
- Vue reactivity: khi thêm/sửa key trong `ref<Record>({})`, dùng spread `ref.value = { ...ref.value, [key]: val }` thay vì mutation `ref.value[key] = val` để đảm bảo trigger reactivity
- Blur + Enter double-fire: khi input bị remove từ DOM (v-if=false), blur event vẫn fire → cần guard flag chống double execution