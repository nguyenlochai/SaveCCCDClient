"""Offline CCCD QR reader. Returns (name, ID, address); never logs QR contents."""
import re
from PIL import Image, ImageOps


class ScanError(ValueError):
    pass


def parse_payload(payload):
    fields = payload.split('|')
    if len(fields) != 7 or not re.fullmatch(r'[0-9]{12}', fields[0]):
        return None
    name = fields[2].strip()
    if (not name or any(ord(c) < 32 for c in name)
            or (fields[1] and not re.fullmatch(r'[0-9]{9}', fields[1]))
            or fields[4] not in ('Nam', 'Nữ')):
        return None
    from datetime import datetime
    for value in (fields[3], fields[6]):
        if not re.fullmatch(r'[0-9]{8}', value):
            return None
        try:
            datetime.strptime(value, '%d%m%Y')
        except ValueError:
            return None
    return name, fields[0], fields[5]


def scan_cccd(path):
    import cv2
    import numpy as np
    try:
        with Image.open(path) as source:
            if source.width * source.height > 24_000_000:
                raise ScanError('Ảnh vượt 24 triệu điểm ảnh. Hãy chọn ảnh nhỏ hơn, chỉ chứa CCCD.')
            image = ImageOps.exif_transpose(source).convert('RGB')
            image.thumbnail((3200, 3200))
        gray = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
        detector = cv2.QRCodeDetector()
        found = set()
        # Native resolution is essential: resizing can break a readable QR.
        # Small crops previously retried the same failing 2x image three times.
        # Deduplicate scales, but scan them all even after success so conflicting
        # decoded identities are not silently ignored. Never crop out other QRs.
        ratios = dict.fromkeys((1.0, *(min(2.0, bound / max(gray.shape))
                                      for bound in (3200, 1600, 800))))
        for ratio in ratios:
            frame = gray if ratio == 1.0 else cv2.resize(
                gray, None, fx=ratio, fy=ratio,
                interpolation=cv2.INTER_NEAREST if ratio > 1 else cv2.INTER_AREA)
            _, payloads, _, _ = detector.detectAndDecodeMulti(frame)
            found.update(value for value in payloads if value)
            value, _, _ = detector.detectAndDecode(frame)
            if value:
                found.add(value)
    except ScanError:
        raise
    except Exception:
        raise ScanError('Không đọc được ảnh hoặc mã QR. Hãy chọn ảnh rõ hơn.') from None
    recognized = {value: parse_payload(value) for value in found if parse_payload(value) is not None}
    identities = set(recognized.values())
    if len(recognized) > 1:
        raise ScanError('Ảnh có nhiều thông tin CCCD khác nhau. Hãy chọn ảnh chỉ có một CCCD.')
    if identities:
        return identities.pop()
    if found:
        raise ScanError('QR không thuộc định dạng CCCD được hỗ trợ (7 trường phân cách bằng |).')
    raise ScanError('Không đọc được mã QR. Chọn ảnh rõ, đủ mã QR; ứng dụng chưa đọc chữ bằng OCR.')
