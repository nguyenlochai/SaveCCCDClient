"""Local storage selection: copy first, validate, then atomically remember it."""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile


def validate_store(directory):
    directory = Path(directory)
    database = directory / 'customers.sqlite3'
    if not directory.is_dir() or not database.is_file() or not (directory / 'images').is_dir():
        raise ValueError(f'Không tìm thấy đầy đủ dữ liệu tại: {directory}. Hãy kết nối lại ổ đĩa / khôi phục thư mục; không tạo dữ liệu trống.')
    connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        if connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError('Cơ sở dữ liệu không toàn vẹn.')
        if connection.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Liên kết ảnh trong cơ sở dữ liệu không hợp lệ.')
        connection.execute('SELECT id,name,phone,cccd,notes,search_text,updated FROM customers LIMIT 1')
        for filename, in connection.execute('SELECT filename FROM images'):
            path = directory / 'images' / filename
            if Path(filename).name != filename or not path.is_file():
                raise ValueError(f'Không tìm thấy ảnh đã lưu: {filename}')
    finally:
        connection.close()


def open_store(base, config_path=None):
    from app import Store
    base = Path(base)
    config_path = Path(config_path) if config_path is not None else base / 'storage.json'
    if not config_path.exists():
        return Store(base / 'data')
    try:
        value = json.loads(config_path.read_text(encoding='utf-8'))['data_directory']
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError('Đường dẫn dữ liệu phải là thư mục tuyệt đối.')
        directory = Path(value)
        validate_store(directory)
        return Store(directory)
    except Exception as exc:
        raise ValueError(f'Không mở được nơi lưu đã chọn ({config_path}): {exc}') from exc


def save_config(config_path, directory):
    config_path = Path(config_path)
    descriptor, temporary = tempfile.mkstemp(prefix='.storage-', suffix='.tmp', dir=config_path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump({'data_directory': str(directory)}, output, ensure_ascii=False, indent=2)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, config_path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def relocate(store, destination, config_path):
    """Return an open validated copy; caller swaps/ closes the old Store on success."""
    from app import Store
    source = store.root.resolve()
    raw = str(destination)
    if '://' in raw or raw.startswith(('\\\\', '//')):
        raise ValueError('Chọn thư mục trên ổ đĩa cục bộ, không dùng URL hoặc ổ mạng.')
    target = Path(destination).resolve()
    if os.name == 'nt':
        import ctypes
        # Reject mapped network drives too, not just explicit UNC paths.
        if ctypes.windll.kernel32.GetDriveTypeW(str(target.anchor)) not in (2, 3):
            raise ValueError('Hãy chọn ổ đĩa cục bộ đang kết nối (không dùng ổ mạng).')
    if target == source:
        raise ValueError('Đây là nơi lưu dữ liệu hiện tại; không cần chuyển.')
    if source in target.parents or target in source.parents:
        raise ValueError('Không chọn thư mục nằm trong hoặc bao quanh nơi lưu hiện tại.')
    if not target.is_dir():
        raise ValueError('Hãy chọn một thư mục cục bộ đã tồn tại và trống.')
    if any(target.iterdir()):
        raise ValueError('Thư mục đích phải trống hoàn toàn; không ghi đè dữ liệu có sẵn.')
    created = []
    candidate = None
    try:
        # Exclusive creation is also a write-permission preflight. Only tracked
        # files/directories are removed on failure, never the chosen folder.
        database = target / 'customers.sqlite3'
        with database.open('xb'):
            created.append(database)
        backup = sqlite3.connect(database)
        try:
            store.db.backup(backup)
        finally:
            backup.close()
        excluded = {'customers.sqlite3', 'customers.sqlite3-wal', 'customers.sqlite3-shm', 'customers.sqlite3-journal'}
        def copy_directory(origin, dest):
            for item in origin.iterdir():
                if origin == source and item.name in excluded:
                    continue
                if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
                    raise ValueError(f'Không sao chép liên kết thư mục/tệp: {item}')
                output = dest / item.name
                if item.is_dir():
                    output.mkdir()
                    created.append(output)
                    copy_directory(item, output)
                else:
                    with item.open('rb') as reader, output.open('xb') as writer:
                        created.append(output)
                        shutil.copyfileobj(reader, writer)
        copy_directory(source, target)
        validate_store(target)
        candidate = Store(target)
        save_config(config_path, target)
        return candidate
    except Exception:
        if candidate is not None:
            candidate.close()
        for path in reversed(created):
            try:
                if path.is_dir():
                    path.rmdir()
                else:
                    path.unlink(missing_ok=True)
            except OSError:
                pass  # Never remove unrelated files to force directory removal.
        raise
