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