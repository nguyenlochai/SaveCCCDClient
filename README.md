# SaveCCCDClient

Ứng dụng Python trên Windows để quản lý hồ sơ và ảnh khách hàng, lưu dữ liệu cục bộ.

## Chạy ứng dụng

Cài Python 3.10+ có Tkinter, sau đó:

```sh
python -m pip install -r requirements.txt
python app.py
```

Hoặc nhấp đúp `MoUngDung.bat` khi máy đã có Python/Tkinter. Launcher tự cài Pillow/OpenCV nếu thiếu bằng đúng Python đang chạy (cần Internet khi cài thư viện; nhận dạng QR chạy offline).

Trong vùng riêng **Quét thông tin CCCD**, bấm **Chọn ảnh** (một ảnh) hoặc **Dán ảnh**, rồi **Quét** để điền tên và CCCD từ QR. Ảnh quét chỉ là ảnh tạm, không vào danh sách ảnh khách hàng, không được lưu/in kể cả khi bấm Lưu; có thể thay hoặc xóa riêng. Không cần có ảnh đính kèm khách hàng. Kiểm tra thông tin rồi bấm Lưu; không OCR, không tự lưu và không xác thực danh tính.

## Chức năng

- Tạo, sửa, xóa hồ sơ khách hàng và lưu nhiều ảnh.
- Tìm theo tên có/không dấu, số điện thoại hoặc CCCD.
- Danh sách phân trang; modal xem đầy đủ thông tin và ảnh.
- Xem trước ảnh để in qua trình duyệt và chọn máy in trước khi xác nhận.
- Chọn thư mục lưu dữ liệu, sao chép dữ liệu cũ an toàn và nhớ lựa chọn.

Xem hướng dẫn chi tiết tại [HUONG_DAN.md](HUONG_DAN.md).

## Dữ liệu và bảo mật

Mặc định dữ liệu nằm trong `data/` cạnh ứng dụng; cấu hình thư mục nằm trong `storage.json`. Thông tin và ảnh chỉ lưu tại máy, chưa mã hóa hoặc bảo vệ bằng mật khẩu ứng dụng. Chỉ thu thập dữ liệu khi có quyền và bảo vệ thư mục lưu trữ.

Repository chỉ chứa mã ứng dụng và hướng dẫn. Không đưa dữ liệu khách hàng, ảnh, cấu hình đường dẫn cá nhân, ảnh chụp kiểm thử hoặc tệp tạm lên Git. `.gitignore` sử dụng danh sách tệp được phép để tránh vô tình thêm thư mục dữ liệu khác.
