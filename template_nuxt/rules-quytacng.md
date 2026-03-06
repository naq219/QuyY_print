# Quy tắc ngầm & Kinh nghiệm (rules-quytacng)

Đây là tài liệu ghi nhận các bài học, quy tắc ngầm rút ra từ các lỗi thực tế trong quá trình phát triển để tránh lặp lại.

## 1. Môi trường Terminal (PowerShell trên Windows)

### 1.1. Lệnh `curl`
- **Vấn đề đã gặp**: Trên PowerShell của Windows, lệnh `curl` mặc định là một alias trỏ đến lệnh `Invoke-WebRequest` của PowerShell, KHÔNG PHẢI là trình `curl` truyền thống ở Linux. Các đối số như `-H` hay `-d` sẽ bị báo lỗi (ví dụ: `Cannot bind parameter 'Headers'`).
- **Giải pháp / Quy tắc ngầm**:
  - Không sử dụng trực tiếp lệnh `curl` khi gọi API qua terminal trên PowerShell.
  - Sử dụng lệnh native của PowerShell: `Invoke-RestMethod` (nhớ parse JSON nếu cần) với các tham số tương ứng `-Uri`, `-Method`, `-Headers`, `-Body`, `-ContentType`.
  - Hoặc nếu bắt buộc phải dùng lệnh curl gốc, hãy gọi rõ file thực thi là `curl.exe` (ví dụ: `curl.exe -s -X POST ...`).

### 1.2. Redirect Output trong PowerShell (`>`)
- **Vấn đề đã gặp**: Ghi đè hoặc nối file bằng pipeline (`| Out-File` hoặc `>`) có thể bị lỗi:
  - Báo lỗi không tìm thấy đường dẫn (ví dụ ghi vào thư mục chưa tồn tại như `C:\tmp`).
  - Lỗi block file hoặc out stream bị lẫn văn bản Unicode (như output của vitest thường có màu sắc hoặc escape sequence gây rối, hoặc báo lỗi stream/encoding).
- **Giải pháp / Quy tắc ngầm**: 
  - Đảm bảo thư mục mục tiêu đã thực sự tồn tại (chạy `mkdir -Force` trước nếu cần thiết).
  - Tốt nhất là sử dụng tool native của agent (viết/đọc file trực tiếp, grep file, v.v.) hơn là cố gắng pipeline text cực đoan trong PowerShell.
  - Test framework như vitest khi chạy liên tục sẽ nhúng file terminal outputs vào. Hãy xài `--reporter=json` và xuất file nếu muốn test script chạy ẩn một cách có kiểm soát.

### 1.3. Lệnh ghép nhiều dòng / command
- **Vấn đề đã gặp**: Ghép command bằng `;` trong PowerShell đôi khi bị ngắt nếu có lỗi (hoặc biến môi trường dính chung luồng lỗi).
- **Giải pháp / Quy tắc ngầm**: Luôn clear và kiểm tra kỹ. Nên tách bạch command ra, hoặc dùng script ps1 nếu tác vụ terminal đòi hỏi nhiều luồng lệnh nối tiếp có error handling (như file `deploy.ps1`).

## 2. Testing Database
- Khi chạy script kiểm tra API (Vitest bypass Nuxt runtime / call API trực tiếp), DB của Turso (nhất là khi test trên dev server) có thể không tự rebuild schema liền (API update code nhưng schema lỗi/khác) dẫn tới Error 500 do Database.
- **Kinh nghiệm**: Test mà tạo dữ liệu dummy CÓ LIÊN QUAN TỚI THAY ĐỔI SCHEMA thì bắt buộc phải chạy `POST /api/init` trước (để trigger code migration). Và test lỗi 500 thì lập tức check Terminal log xem SQL query sai ở cấu trúc cột nào, không kết luận vội là sai code route.
