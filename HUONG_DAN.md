# SaveCCCD — Quản lý khách hàng

## Mở ứng dụng
- Trên máy hiện tại: nhấp đúp **MoUngDung.bat**.
- Hoặc mở terminal trong thư mục này, chạy `python app.py`.
- Máy khác: cài Python 3.10+ có Tkinter, chạy `python -m pip install -r requirements.txt` rồi `python app.py`.

## Sử dụng
1. Bấm **Tạo khách hàng mới**, nhập tên và ít nhất SĐT hoặc CCCD.
2. Bấm **Chọn ảnh**; có thể chọn nhiều ảnh chân dung, mặt trước / sau CCCD. Hỗ trợ JPG, PNG, WEBP, BMP.
3. Bấm **Lưu khách hàng** hoặc Ctrl+S. Ảnh được sao chép, không phụ thuộc ảnh gốc sau khi lưu.
4. Nhập một phần tên, SĐT hoặc CCCD vào ô tìm kiếm. Tên hỗ trợ tìm không dấu; Ctrl+F đưa con trỏ vào ô tìm.
5. Chọn khách hàng để xem, sửa thông tin hoặc thêm ảnh. Chọn tên ảnh để xem trước; nhấp đúp để mở ảnh gốc.
6. **Bỏ ảnh chưa lưu** chỉ bỏ ảnh vừa chọn, không xóa ảnh đã lưu.

CCCD phải đủ 12 chữ số, giữ nguyên số 0 đầu. Không cho tạo trùng CCCD. SĐT có thể dùng chung giữa các khách hàng. Ứng dụng chỉ kiểm tra định dạng, không xác minh danh tính hay tính hợp lệ thực tế của CCCD.

## Dữ liệu nằm ở đâu?
Mặc định là thư mục `data` cạnh `app.py`. Dòng **Nơi lưu** ở chân cửa sổ luôn hiển thị đường dẫn đang dùng (có thể chọn/sao chép hoặc di chuyển con trỏ để đọc đường dẫn dài).

- Bấm **Chọn nơi lưu dữ liệu**, chọn một thư mục **trống** trên ổ D:, E: hoặc ổ cục bộ khác, rồi xác nhận. Đây là nơi lưu chung cho **tất cả khách hàng**, không phải thư mục riêng từng người và không nhận đường dẫn web.
- Ứng dụng sao chép toàn bộ cơ sở dữ liệu SQLite, ảnh và thư mục xem trước in; chỉ chuyển sang nơi mới sau khi kiểm tra bản sao. **Giữ nguyên dữ liệu cũ** để làm bản sao lưu; dữ liệu mới phát sinh chỉ ghi tại nơi mới.
- Lưu chỉnh sửa đang làm trước khi chuyển. Nếu đồng ý bỏ chỉnh sửa, chúng chỉ bị bỏ sau khi chuyển thành công. Hủy hoặc lỗi chuyển không làm mất bản nháp.
- Không chọn thư mục có sẵn dữ liệu hoặc thư mục nằm trong/bao quanh nơi lưu hiện tại. Không ghi đè dữ liệu đích.
- Đường dẫn được ghi vào `storage.json` cạnh `app.py` và nhớ khi mở lại. Nếu ổ đĩa/thư mục đã chọn mất kết nối hoặc dữ liệu lỗi, ứng dụng báo lỗi và dừng, **không tự mở dữ liệu trống**. Kết nối lại đúng ổ đĩa hoặc khôi phục thư mục đầy đủ rồi mở lại; không xóa cấu hình để xử lý lỗi mất kết nối.

Trong nơi lưu: `customers.sqlite3` chứa hồ sơ và liên kết ảnh; `images/` chứa ảnh đặt tên ngẫu nhiên; `print-preview/` chứa bản xem trước in nếu có. Không đổi tên hoặc xóa riêng ảnh. Không có kết nối mạng hay tải dữ liệu lên máy chủ.

## Sao lưu và bảo mật
- Đóng ứng dụng rồi sao chép **toàn bộ thư mục đang hiển thị ở Nơi lưu** sang nơi an toàn. Để khôi phục, đóng ứng dụng và thay nội dung nơi lưu bằng bản sao lưu đầy đủ. Giữ lại bản hiện tại trước khi thay. Không chạy nhiều phiên ứng dụng khi chuyển nơi lưu.
- Đây là bản dùng cục bộ, **chưa có mật khẩu ứng dụng hoặc mã hóa dữ liệu**. Người có quyền đọc thư mục có thể đọc hồ sơ và ảnh.
- Chỉ lưu ảnh khi có quyền / sự đồng ý cần thiết. Bảo vệ tài khoản Windows, hạn chế quyền truy cập, cân nhắc BitLocker. Không đưa data lên Git hoặc thư mục công khai.
- Không thiết kế cho nhiều máy cùng ghi dữ liệu qua ổ mạng. Cột **Thao tác** có **Chi tiết / Sửa / Xóa**. Chi tiết mở modal hiển thị tên, SĐT, CCCD, mã hồ sơ, thời gian cập nhật UTC, ghi chú đầy đủ và danh sách tất cả ảnh (chọn từng ảnh để xem hoặc mở ảnh gốc). Nút Sửa đưa hồ sơ vào form bên phải. Xóa yêu cầu xác nhận, xóa vĩnh viễn hồ sơ cùng ảnh; nếu tệp ảnh không xóa được, ứng dụng cảnh báo các đường dẫn còn lại. Nên sao lưu trước khi xóa.

## Kiểm thử
`python -B -m unittest discover -s tests -v`

Kiểm thử dùng dữ liệu tổng hợp trong tests, không thêm khách giả vào data thật. Bao gồm lưu và mở lại SQLite, ảnh sao chép độc lập, tìm kiếm, sửa, kiểm tra nhập liệu/trùng CCCD, rollback khi ảnh lỗi và thao tác trên cửa sổ Tk thật.
