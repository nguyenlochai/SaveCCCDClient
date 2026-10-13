# SaveCCCD — Quản lý khách hàng

## Mở ứng dụng
- Trên máy hiện tại: nhấp đúp **MoUngDung.bat**.
- Hoặc mở terminal trong thư mục này, chạy `python app.py`.
- Máy khác: cài Python 3.10+ có Tkinter, chạy `python -m pip install -r requirements.txt` rồi `python app.py`.

## Sử dụng
1. Bấm **Tạo khách hàng mới**, nhập tên và ít nhất SĐT hoặc CCCD. Ô **Địa chỉ** nằm dưới CCCD, trên Ghi chú, có thể để trống; không thêm cột vào bảng danh sách.
2. Bấm **Chọn ảnh**; có thể chọn nhiều ảnh chân dung, mặt trước / sau CCCD. Hỗ trợ JPG, PNG, WEBP, BMP.
   - **Dán ảnh chụp màn hình:** nhấn **Win+Shift+S**, khoanh vùng cần chụp, quay lại SaveCCCD rồi bấm **Dán ảnh** cạnh nút xóa ảnh. Không cần tự lưu ảnh ra tệp.
   - Hoặc nhấp vùng xem trước / danh sách ảnh (có thể dùng Tab để chọn vùng Chọn ảnh), rồi nhấn **Ctrl+V**. Ctrl+V trong ô tên, SĐT, CCCD, tìm kiếm và ghi chú vẫn dán văn bản bình thường.
   - Mỗi lần dán tạo một ảnh PNG riêng trong danh sách **[Chưa lưu]** và hiện xem trước. Có thể dán nhiều lần, kết hợp với **Chọn ảnh**. Clipboard trống, văn bản hoặc danh sách tệp sẽ có thông báo; muốn thêm ảnh từ ổ đĩa hãy dùng **Chọn ảnh**.
3. Bấm **Lưu khách hàng** hoặc Ctrl+S. Ảnh được sao chép, không phụ thuộc ảnh gốc sau khi lưu.
4. Nhập một phần tên, SĐT hoặc CCCD vào ô tìm kiếm. Tên hỗ trợ tìm không dấu; Ctrl+F đưa con trỏ vào ô tìm.
5. Chọn khách hàng để xem, sửa thông tin hoặc thêm ảnh. Chọn tên ảnh để xem trước; nhấp đúp để mở ảnh gốc.
6. Chọn ảnh rồi bấm **Xóa ảnh đã chọn** trong form hoặc cửa sổ Chi tiết. Ảnh đã lưu yêu cầu xác nhận có tên tệp và bị xóa ngay, không cần bấm Lưu; chỉ ảnh được chọn bị xóa, không xóa khách hàng hay các ảnh khác. Chỉnh sửa thông tin và ảnh đang chờ lưu được giữ nguyên. Với ảnh **[Chưa lưu]**, nút chỉ bỏ khỏi danh sách chờ, không xóa tệp gốc. Nếu tệp đã lưu không xóa được, ứng dụng báo lỗi và giữ liên kết ảnh để thử lại; tệp vốn đã mất thì liên kết được dọn bỏ.

Xóa ảnh không xóa các bản sao lưu hoặc bản xem trước in đã tạo trước đó trong `print-preview/`. Các bản này cần được quản lý riêng. Cửa sổ đang chạy cần được đóng/mở lại để nhận bản cập nhật ứng dụng (hãy lưu bản nháp trước).

CCCD phải đủ 12 chữ số, giữ nguyên số 0 đầu. Không cho tạo trùng CCCD. SĐT có thể dùng chung giữa các khách hàng. Ứng dụng chỉ kiểm tra định dạng, không xác minh danh tính hay tính hợp lệ thực tế của CCCD.

Ảnh dán được giữ trong thư mục tạm cục bộ `SaveCCCD-paste-*` của Windows đến khi lưu thành công. Khi lưu, ảnh được sao chép vào **Nơi lưu** đang chọn; sau đó tệp tạm được dọn. Bỏ ảnh, đồng ý bỏ bản nháp, chuyển hồ sơ hoặc đóng ứng dụng cũng dọn ảnh tạm, không xóa tệp gốc đã chọn từ ổ đĩa. Hủy bỏ bản nháp hoặc lỗi lưu/chuyển nơi lưu giữ nguyên ảnh chờ để thử lại. Nếu tệp tạm bị ứng dụng khác khóa, SaveCCCD cảnh báo đường dẫn để dọn sau. Thoát cưỡng bức/mất điện có thể để lại tệp tạm; bản nháp chưa lưu không được phục hồi tự động. Tất cả xử lý ở máy Windows, không tải ảnh lên mạng.

## Quét thông tin CCCD từ ảnh (QR cục bộ)
- Dùng vùng riêng **Quét thông tin CCCD**: **Chọn ảnh** chỉ chọn một ảnh; **Dán ảnh** nhận ảnh chụp Win+Shift+S; **Quét** đọc ảnh đang xem trước. Chọn/dán lần nữa thay ảnh cũ; **Xóa ảnh quét** xóa ảnh tạm. Hủy hộp chọn giữ ảnh trước. Ctrl+V khi focus vùng quét chỉ thay ảnh quét; các ô nhập vẫn dán văn bản.
- Vùng **Ảnh khách hàng** bên dưới hoàn toàn độc lập, vẫn chọn/dán nhiều ảnh để lưu và in. Quét không dùng ảnh đang chọn trong danh sách này, không thêm ảnh vào danh sách và hoạt động cả khi hồ sơ không có ảnh đính kèm. Ở cửa sổ thấp, cuộn form để thấy vùng quét; Lưu và Nơi lưu luôn hiện ở chân cửa sổ.
- Ảnh quét được sao chép vào thư mục tạm riêng `SaveCCCD-scan-*`, không lưu vào hồ sơ hoặc bản in kể cả sau khi Lưu. Ảnh tạm được dọn khi thay/xóa, lưu thành công, bỏ form, chuyển khách hàng/nơi lưu thành công hoặc đóng ứng dụng; ảnh gốc trên ổ đĩa không bị xóa. Lỗi quét/lưu giữ ảnh để thử lại. Tệp bị khóa sẽ có cảnh báo và được thử dọn lại; thoát cưỡng bức/mất điện có thể để lại thư mục tạm cần dọn thủ công.
- Khi thành công, form cuộn lên và điền **Tên khách hàng / Số CCCD / Địa chỉ**; giữ SĐT, ghi chú và các ảnh. Địa chỉ giữ nguyên dấu và nội dung QR, số 0 đầu CCCD được giữ nguyên. Nếu tên/CCCD/địa chỉ hiện tại khác, ứng dụng hỏi trước khi thay. QR có trường địa chỉ trống không xóa địa chỉ đang nhập và không tự suy đoán địa chỉ.
- Kiểm tra lại rồi bấm **Lưu khách hàng**: quét không tự lưu, không xác thực danh tính. Nếu đổi ảnh/hồ sơ hoặc sửa form trong lúc quét, kết quả cũ bị bỏ.
- Chỉ hỗ trợ QR 7 trường: `CCCD|CMND cũ|Họ tên|Ngày sinh|Giới tính|Địa chỉ|Ngày cấp`. CCCD đúng 12 chữ số ASCII; CMND cũ trống hoặc 9 chữ số; tên không trống; địa chỉ có thể trống; giới tính `Nam`/`Nữ`; hai ngày hợp lệ dạng `ddMMyyyy`. Định dạng khác, URL và QR có nhiều payload CCCD khác nhau sẽ không điền tự động.
- Chưa có OCR. Ảnh không đọc được QR hoặc ảnh mờ/QR quá nhỏ không làm thay đổi thông tin; hãy chụp rõ một CCCD, đủ viền QR. Giới hạn ảnh 24 triệu điểm ảnh, quét ở kích thước gốc (tối đa cạnh 3200 px) và các tỷ lệ khác nhau; không chỉ phóng to ảnh QR nhỏ. Không đảm bảo đọc mọi QR hỏng hoặc nhận ra QR không giải mã được.
- Xử lý ảnh hoàn toàn tại máy bằng OpenCV, không gửi ảnh/payload lên mạng. `MoUngDung.bat` kiểm tra thư viện và cài thư viện còn thiếu bằng đúng Python đang dùng (bước cài đặt cần Internet; quét không cần Internet).

## Dữ liệu nằm ở đâu?
Mặc định là thư mục `data` cạnh `app.py`. Dòng **Nơi lưu** ở chân cửa sổ luôn hiển thị đường dẫn đang dùng (có thể chọn/sao chép hoặc di chuyển con trỏ để đọc đường dẫn dài).

- Bấm **Chuyển dữ liệu…**, chọn một thư mục **trống** trên ổ D:, E: hoặc ổ cục bộ khác, rồi xác nhận. Đây là nơi lưu chung cho **tất cả khách hàng**, không phải thư mục riêng từng người và không nhận đường dẫn web. Nút này không chuyển dữ liệu lên ổ mạng.
- Ứng dụng sao chép toàn bộ cơ sở dữ liệu SQLite, ảnh và thư mục xem trước in; chỉ chuyển sang nơi mới sau khi kiểm tra bản sao. **Giữ nguyên dữ liệu cũ** để làm bản sao lưu; dữ liệu mới phát sinh chỉ ghi tại nơi mới.
- Lưu chỉnh sửa đang làm trước khi chuyển. Nếu đồng ý bỏ chỉnh sửa, chúng chỉ bị bỏ sau khi chuyển thành công. Hủy hoặc lỗi chuyển không làm mất bản nháp.
- Không chọn thư mục có sẵn dữ liệu hoặc thư mục nằm trong/bao quanh nơi lưu hiện tại. Không ghi đè dữ liệu đích.
- Đường dẫn được ghi vào `storage.json` cạnh `app.py` và nhớ khi mở lại. Nếu ổ đĩa/thư mục đã chọn mất kết nối hoặc dữ liệu lỗi, ứng dụng báo lỗi và dừng, **không tự mở dữ liệu trống**. Kết nối lại đúng ổ đĩa hoặc khôi phục thư mục đầy đủ rồi mở lại; không xóa cấu hình để xử lý lỗi mất kết nối.

### Mở dữ liệu có sẵn (kể cả thư mục chia sẻ LAN)
- Bấm **Mở dữ liệu có sẵn** ở chân cửa sổ, chọn đúng thư mục chứa cả `customers.sqlite3` và `images/`, đọc cảnh báo rồi xác nhận. Có thể chọn đường dẫn UNC `\\192.168.9.227\data` hoặc ổ mạng đã ánh xạ. Thư mục phải có dữ liệu hợp lệ từ trước; nút này không tạo cơ sở dữ liệu mới, không sao chép hay ghi đè bằng dữ liệu hiện tại.
- Ứng dụng kiểm tra dữ liệu/ảnh, mở trực tiếp tại nơi chọn và nhớ đường dẫn trong `storage.json`. Lỗi mở hoặc lỗi ghi cấu hình giữ nơi lưu và bản nháp hiện tại. Hồ sơ cũ thiếu cột địa chỉ sẽ được bổ sung cột khi kích hoạt thành công.
- Máy chủ phải đang bật, mạng ổn định và tài khoản Windows phải có quyền đọc/ghi thư mục cùng tệp. Nếu dữ liệu đang bận/bị khóa, dừng thao tác ghi ở máy khác rồi thử lại. Không xóa tệp khóa/journal để ép mở. Nếu mất kết nối, kết nối lại đúng nơi lưu; không tạo bản dữ liệu trống thay thế.
- **SQLite qua SMB không bảo đảm an toàn khi nhiều máy cùng ghi. Không chỉnh sửa đồng thời**, kể cả hai hồ sơ khác nhau; các thao tác lưu/xóa ảnh cũng là ghi dữ liệu. Thời gian chờ khóa SQLite không phải cơ chế bảo đảm an toàn nhiều máy. Muốn vận hành nhiều người ghi đồng thời cần dịch vụ trung tâm quản lý truy cập, không chỉ chia sẻ tệp SQLite.
- Dữ liệu đang ở chế độ WAL bị từ chối khi mở theo cách này. Nhờ người quản trị chuyển sang journal DELETE tại máy chủ sau khi đóng tất cả phiên; không tự xóa các tệp WAL/SHM.

Trong nơi lưu: `customers.sqlite3` chứa hồ sơ và liên kết ảnh; `images/` chứa ảnh đặt tên ngẫu nhiên; `print-preview/` chứa bản xem trước in nếu có. Không đổi tên hoặc xóa riêng ảnh. Khi dùng thư mục chia sẻ, các tệp này được đọc/ghi qua mạng LAN; không có dịch vụ máy chủ điều phối ghi đồng thời.

Hồ sơ cũ được bổ sung cột SQLite `address` với mặc định trống khi mở ứng dụng; migration chỉ thêm cột nếu chưa có, giữ nguyên các trường cũ và ảnh.

## Sao lưu và bảo mật
- Đóng ứng dụng **trên tất cả máy đang dùng nơi lưu đó**, rồi sao chép **toàn bộ thư mục đang hiển thị ở Nơi lưu** sang nơi an toàn, độc lập với máy chủ/ổ đĩa gốc. Sao lưu thường xuyên và kiểm tra khả năng khôi phục. Để khôi phục, đóng tất cả phiên và thay nội dung nơi lưu bằng bản sao lưu đầy đủ, hoặc dùng **Mở dữ liệu có sẵn** để mở thư mục đã khôi phục. Giữ lại bản hiện tại trước khi thay. Không chạy nhiều phiên ứng dụng khi chuyển nơi lưu.
- Ứng dụng **chưa có mật khẩu ứng dụng hoặc mã hóa dữ liệu**. Người có quyền đọc thư mục cục bộ/chia sẻ có thể đọc hồ sơ và ảnh; giới hạn quyền chia sẻ SMB cho đúng người dùng.
- Chỉ lưu ảnh khi có quyền / sự đồng ý cần thiết. Bảo vệ tài khoản Windows, hạn chế quyền truy cập, cân nhắc BitLocker. Không đưa data lên Git hoặc thư mục công khai.
- Không thiết kế cho nhiều máy cùng ghi dữ liệu qua ổ mạng. Cột **Thao tác** có **Chi tiết / Sửa / Xóa**. Chi tiết mở modal hiển thị tên, SĐT, CCCD, mã hồ sơ, thời gian cập nhật UTC, địa chỉ và ghi chú đầy đủ (xuống dòng, chỉ đọc, có thanh cuộn) và danh sách tất cả ảnh (chọn từng ảnh để xem hoặc mở ảnh gốc). Nút Sửa đưa hồ sơ vào form bên phải. Xóa yêu cầu xác nhận, xóa vĩnh viễn hồ sơ cùng ảnh; nếu tệp ảnh không xóa được, ứng dụng cảnh báo các đường dẫn còn lại. Nên sao lưu trước khi xóa.

## Kiểm thử
Cài phụ thuộc kiểm thử: `python -m pip install -r requirements-test.txt` (hoặc `uv pip install --python "đường dẫn python.exe" -r requirements-test.txt` nếu môi trường không có pip). `qrcode` chỉ dùng tạo fixture tổng hợp, không cần cho ứng dụng.

`python -B -m unittest discover -s tests -v`

Kiểm thử dùng dữ liệu tổng hợp trong tests, không thêm khách giả vào data thật. Bao gồm lưu và mở lại SQLite, ảnh sao chép độc lập, tìm kiếm, sửa, kiểm tra nhập liệu/trùng CCCD, rollback khi ảnh lỗi và thao tác trên cửa sổ Tk thật.
