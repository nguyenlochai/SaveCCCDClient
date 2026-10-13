"""Local-only image print preview. Never submits directly to a printer."""
import base64
import io
from os import PathLike
from pathlib import Path
import webbrowser
from PIL import Image, ImageOps


def prepare_preview(source, directory):
    """Embed a single source or an ordered iterable, two photos per A4 sheet."""
    sources = [source] if isinstance(source, (str, bytes, PathLike)) or hasattr(source, 'read') else list(source)
    if not sources:
        raise ValueError('Chưa có ảnh đã lưu để in.')
    photos = []
    for item in sources:
        with Image.open(item) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
        encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
        photos.append(f'<img alt="Ảnh {len(photos) + 1}" src="data:image/png;base64,{encoded}">')
    sheets = ''.join('<section class="sheet">' + ''.join(photos[i:i + 2]) + '</section>'
                     for i in range(0, len(photos), 2))
    count = f'{len(photos)} ảnh · {(len(photos) + 1) // 2} trang A4'
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / 'anh-in.html'
    target.write_text('''<!doctype html><html lang="vi"><meta charset="utf-8">
<title>In ảnh khách hàng</title><style>
body{margin:0;background:#edf4fb;font:15px "Segoe UI",sans-serif;color:#193657}
header{padding:20px;text-align:center}button{background:#1677ee;color:white;border:0;border-radius:8px;padding:12px 25px;font:inherit;cursor:pointer}
p{line-height:1.6}
.sheet{box-sizing:content-box;background:white;margin:0 auto 24px;padding:10mm;width:190mm;height:276mm;display:flex;flex-direction:column;gap:6mm}
:root{--photo-width:85.6mm;--photo-height:54mm}
img{display:block;width:85.6mm;height:54mm;width:var(--photo-width);height:var(--photo-height);min-height:0;flex:0 0 var(--photo-height);object-fit:contain;align-self:center}
.controls{display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin:12px auto}
.controls input{width:75px;padding:7px;font:inherit}
@page{size:A4 portrait;margin:10mm}
@media print{header{display:none}body{background:white}.sheet{margin:0;padding:0;break-inside:avoid;break-after:page}.sheet:last-child{break-after:auto}}
</style><header><h2>In ảnh khách hàng</h2>
<p><strong>''' + count + '''</strong> · 2 ảnh mỗi trang, xếp trên / dưới.</p>
<div class="controls"><label>Rộng (mm) <input id="photo-width" type="number" min="30" max="180" step="0.1" value="85.6"></label>
<label>Cao (mm) <input id="photo-height" type="number" min="20" max="125" step="0.1" value="54"></label>
<button type="button" onclick="window.print()">Chọn máy in / In ảnh</button></div>
<p>In tất cả ảnh đã lưu của khách hàng. Chọn máy in và số bản trong hộp thoại in.<br>
Khổ A4, chiều dọc; tỷ lệ in 100%. Mặc định mỗi ảnh nằm trong khung 8,56 × 5,4 cm; chỉnh kích thước phía trên để xem trước và in.<br>
Ảnh giữ nguyên tỷ lệ, không cắt; nếu ảnh có nền dư thì phần thẻ sẽ nhỏ hơn khung.<br>
Tắt đầu trang/chân trang nếu trình duyệt đang bật.<br>
Chỉ in sau khi xác nhận. Đóng tab này khi sử dụng xong.</p></header>
<main>''' + sheets + '''</main><script>
for (const [id, property] of [['photo-width', '--photo-width'], ['photo-height', '--photo-height']]) {
  const input = document.getElementById(id);
  input.addEventListener('input', () => {
    const value = Number(input.value);
    if (Number.isFinite(value) && value >= Number(input.min) && value <= Number(input.max)) {
      document.documentElement.style.setProperty(property, value + 'mm');
    }
  });
  input.addEventListener('change', () => {
    const value = Number(input.value);
    if (!Number.isFinite(value)) return;
    input.value = Math.min(Number(input.max), Math.max(Number(input.min), value));
    document.documentElement.style.setProperty(property, input.value + 'mm');
  });
}
</script></html>''', encoding='utf-8')
    return target


def open_print_preview(source, directory):
    target = prepare_preview(source, directory)
    if not webbrowser.open(target.resolve().as_uri()):
        raise OSError('Không mở được trình duyệt. Bản in nằm tại: ' + str(target))
    return target
