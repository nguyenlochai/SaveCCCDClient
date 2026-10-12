"""Local-only image print preview. Never submits directly to a printer."""
import base64
import io
from pathlib import Path
import webbrowser
from PIL import Image, ImageOps


def prepare_preview(source, directory):
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        image = image.convert('RGB')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / 'anh-in.html'
    target.write_text('''<!doctype html><html lang="vi"><meta charset="utf-8">
<title>In ảnh khách hàng</title><style>
body{margin:0;background:#edf4fb;font:15px "Segoe UI",sans-serif;color:#193657}
header{padding:20px;text-align:center}button{background:#1677ee;color:white;border:0;border-radius:8px;padding:12px 25px;font:inherit;cursor:pointer}
p{line-height:1.6}main{background:white;margin:0 auto 24px;padding:10mm;max-width:190mm}
img{display:block;width:100%;height:250mm;object-fit:contain}
@page{size:auto;margin:10mm}
@media print{header{display:none}body{background:white}main{margin:0;padding:0;max-width:none}img{width:100%;height:90vh;object-fit:contain;break-inside:avoid}}
</style><header><h2>In ảnh khách hàng</h2>
<button onclick="window.print()">Chọn máy in / In ảnh</button>
<p>Chọn khổ giấy, chiều giấy và số bản trong hộp thoại in.<br>
Ảnh giữ nguyên tỷ lệ, không cắt. Tắt đầu trang/chân trang nếu trình duyệt đang bật.<br>
Chỉ in sau khi xác nhận. Đóng tab này khi sử dụng xong.</p></header>
<main><img alt="Ảnh được chọn để in" src="data:image/png;base64,'''+encoded+'''"></main></html>''', encoding='utf-8')
    return target


def open_print_preview(source, directory):
    target = prepare_preview(source, directory)
    if not webbrowser.open(target.resolve().as_uri()):
        raise OSError('Không mở được trình duyệt. Bản in nằm tại: ' + str(target))
    return target
