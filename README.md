# SaveCCCDClient

Ứng dụng Python trên Windows để quản lý hồ sơ và ảnh khách hàng, lưu dữ liệu cục bộ.

## Chạy ứng dụng

Cài Python 3.10+ có Tkinter, sau đó:

```sh
python -m pip install -r requirements.txt
python app.py
```

Hoặc nhấp đúp `MoUngDung.bat` khi máy đã có Python và Pillow.

## Chức năng

- Tạo, sửa, xóa hồ sơ khách hàng và lưu nhiều ảnh.
- Tìm theo tên có/không dấu, số điện thoại hoặc CCCD.
- Danh sách phân trang; modal xem đầy đủ thông tin và ảnh.
- Xem trước ảnh để in qua trình duyệt và chọn máy in trước khi xác nhận.
- Chọn thư mục lưu dữ liệu, sao chép dữ liệu cũ an toàn và nhớ lựa chọn.

Xem hướng dẫn chi tiết tại [HUONG_DAN.md](HUONG_DAN.md).

## Dữ liệu và bảo mật

Mặc định dữ liệu nằm trong `data/` cạnh ứng dụng; cấu hình thư mục nằm trong `storage.json`. Thông tin và ảnh chỉ lưu tại máy, chưa mã hóa hoặc bảo vệ bằng mật khẩu ứng dụng. Chỉ thu thập dữ liệu khi có quyền và bảo vệ thư mục lưu trữ.

Repository chỉ chứa mã ứng dụng và hướng dẫn. Không đưa dữ liệu khách hàng, ảnh, cấu hình đường dẫn cá nhân, mã kiểm thử, ảnh chụp kiểm thử hoặc tệp tạm lên Git. `.gitignore` sử dụng danh sách tệp được phép để tránh vô tình thêm thư mục dữ liệu khác.
