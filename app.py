"""Quản lý khách hàng cục bộ. Chạy: python app.py"""
from pathlib import Path
import sqlite3
import unicodedata
import uuid
import shutil
import tempfile
from PIL import Image, ImageGrab

BASE = Path(__file__).resolve().parent


def normalize(value):
    value = value.lower().replace('đ', 'd')
    return ''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.combining(c))


class Store:
    def __init__(self, directory, *, existing=False):
        from storage import connect_database
        self.root = Path(directory)
        if not existing:
            (self.root / 'images').mkdir(parents=True, exist_ok=True)
        self.db = connect_database(self.root / 'customers.sqlite3', 'rw' if existing else 'rwc')
        try:
            self._initialize(existing)
        except Exception:
            self.db.close()
            raise

    def _initialize(self, existing):
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        if existing and self.db.execute('PRAGMA journal_mode').fetchone()[0] == 'wal':
            raise ValueError('Dữ liệu đang dùng WAL. Hãy đóng các ứng dụng và chuyển sang journal DELETE tại máy chủ trước khi mở qua mạng.')
        if not existing:
            self.db.executescript('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL,
                cccd TEXT NOT NULL, notes TEXT NOT NULL, search_text TEXT NOT NULL,
                updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                filename TEXT NOT NULL, original_name TEXT NOT NULL);
        ''')

        # Keep the old column order and all existing rows/attachments intact.
        columns = {row['name'] for row in self.db.execute('PRAGMA table_info(customers)')}
        if 'address' not in columns:
            # Existing-folder activation commits this only after config succeeds.
            self.db.execute('BEGIN IMMEDIATE')
            self.db.execute("ALTER TABLE customers ADD COLUMN address TEXT NOT NULL DEFAULT ''")
            if not existing:
                self.db.commit()

    def rotate_image(self, customer_id, image_id):
        """Atomically replace one owned saved photo with its clockwise rotation."""
        with self.db:
            image = self.db.execute('SELECT * FROM images WHERE customer_id=? AND id=?',
                                    (customer_id, image_id)).fetchone()
            if image is None:
                raise ValueError('Ảnh không còn tồn tại hoặc không thuộc khách hàng này.')
            target = self.image_path(image)
            temporary = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
            try:
                with Image.open(target) as source:
                    rotated = ImageOps.exif_transpose(source).transpose(Image.Transpose.ROTATE_270)
                    fmt = source.format if source.format in ('PNG', 'JPEG', 'WEBP', 'BMP') else 'PNG'
                    rotated.save(temporary, format=fmt)
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)

    def save(self, customer_id, name, phone, cccd, notes, photos=(), *, address='', photo_rotations=None):
        import re
        name, cccd = name.strip(), cccd.strip()
        phone = re.sub(r'[\s.()-]', '', phone.strip())
        if not name:
            raise ValueError('Vui lòng nhập tên khách hàng.')
        if not phone and not cccd:
            raise ValueError('Nhập ít nhất SĐT hoặc CCCD để tra cứu.')
        if phone and not re.fullmatch(r'\+?[0-9]{9,15}', phone):
            raise ValueError('SĐT phải có 9–15 chữ số, có thể bắt đầu bằng +.')
        if cccd and not re.fullmatch(r'[0-9]{12}', cccd):
            raise ValueError('CCCD phải gồm đúng 12 chữ số.')
        if cccd and self.db.execute('SELECT id FROM customers WHERE cccd=? AND id<>?', (cccd, customer_id or '')).fetchone():
            raise ValueError('CCCD này đã tồn tại. Hãy tìm và sửa khách hàng cũ.')
        customer_id = customer_id or uuid.uuid4().hex
        copied = []
        try:
            with self.db:
                self.db.execute('''INSERT INTO customers(id,name,phone,cccd,notes,search_text,address)
                    VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,phone=excluded.phone,cccd=excluded.cccd,
                    notes=excluded.notes,search_text=excluded.search_text,address=excluded.address,updated=CURRENT_TIMESTAMP''',
                    (customer_id, name, phone, cccd, notes, normalize(f'{name} {phone} {cccd}'), address))
                for source in photos:
                    source = Path(source)
                    with Image.open(source) as image:
                        image.verify()
                    image_id = uuid.uuid4().hex
                    filename = image_id + source.suffix.lower()
                    target = self.root / 'images' / filename
                    copied.append(target)
                    turns = (photo_rotations or {}).get(source, 0) % 4
                    if turns:
                        with Image.open(source) as original:
                            rotated = ImageOps.exif_transpose(original).transpose(
                                (Image.Transpose.ROTATE_270, Image.Transpose.ROTATE_180,
                                 Image.Transpose.ROTATE_90)[turns - 1])
                            fmt = original.format if original.format in ('PNG', 'JPEG', 'WEBP', 'BMP') else 'PNG'
                            rotated.save(target, format=fmt)
                    else:
                        shutil.copyfile(source, target)
                    self.db.execute('INSERT INTO images VALUES(?,?,?,?)',
                                    (image_id, customer_id, filename, source.name))
        except Exception:
            for path in copied:
                path.unlink(missing_ok=True)
            raise
        return customer_id

    def search(self, query=''):
        query = normalize(query.strip())
        return self.db.execute('SELECT * FROM customers WHERE instr(search_text,?)>0 ORDER BY updated DESC,name', (query,)).fetchall()

    def search_page(self, query='', page=1, page_size=20):
        query = normalize(query.strip())
        total = self.db.execute('SELECT COUNT(*) FROM customers WHERE instr(search_text,?)>0', (query,)).fetchone()[0]
        pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, pages))
        rows = self.db.execute('''SELECT * FROM customers WHERE instr(search_text,?)>0
            ORDER BY updated DESC,name,id LIMIT ? OFFSET ?''',
            (query, page_size, (page - 1) * page_size)).fetchall()
        return rows, total, page, pages

    def get(self, customer_id):
        return (self.db.execute('SELECT * FROM customers WHERE id=?', (customer_id,)).fetchone(),
                self.db.execute('SELECT * FROM images WHERE customer_id=? ORDER BY rowid', (customer_id,)).fetchall())

    def image_path(self, image):
        return self.root / 'images' / image['filename']

    def delete_image(self, customer_id, image_id):
        """Remove only an owned attachment; keep its row if unlink fails."""
        with self.db:
            image = self.db.execute(
                'SELECT * FROM images WHERE customer_id=? AND id=?',
                (customer_id, image_id)).fetchone()
            if image is None:
                raise ValueError('Ảnh không còn tồn tại hoặc không thuộc khách hàng này.')
            self.image_path(image).unlink(missing_ok=True)
            self.db.execute('DELETE FROM images WHERE customer_id=? AND id=?',
                            (customer_id, image_id))

    def delete(self, customer_id):
        _, images = self.get(customer_id)
        with self.db:
            self.db.execute('DELETE FROM customers WHERE id=?', (customer_id,))
        failed = []
        for image in images:
            try:
                self.image_path(image).unlink(missing_ok=True)
            except OSError:
                failed.append(str(self.image_path(image)))
        return failed

    def close(self):
        self.db.close()


import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, ImageOps


def confirm_photo_deletion(parent, store, customer_id, image):
    if not messagebox.askyesno('Xác nhận xóa ảnh',
            f"Xóa vĩnh viễn ảnh đã lưu: {image['original_name']}?\n\n"
            'Chỉ ảnh này bị xóa ngay; khách hàng và các ảnh khác được giữ nguyên. '
            'Không thể hoàn tác.', icon='warning', default='no', parent=parent):
        return False
    try:
        store.delete_image(customer_id, image['id'])
    except Exception as exc:
        messagebox.showerror('Không thể xóa ảnh', str(exc), parent=parent)
        return False
    return True


class DetailDialog(tk.Toplevel):
    def __init__(self, parent, store, record, images, on_photo_deleted=None):
        super().__init__(parent)
        self.customer_id = record['id']
        self.on_photo_deleted = on_photo_deleted
        from detail_layout import build_detail
        build_detail(self, parent, store, record, images)

    def delete_photo(self):
        selected = self.photo_list.curselection()
        if not selected:
            return
        index = selected[0]
        image = self.images[index]
        if not confirm_photo_deletion(self, self.store, self.customer_id, image):
            return
        self.images.pop(index)
        self.photo_list.delete(0, 'end')
        for number, item in enumerate(self.images, 1):
            self.photo_list.insert('end', f"{number}. {item['original_name']}")
        self.photo_count.configure(text=f'Ảnh đã lưu ({len(self.images)})')
        self.preview_image = None
        self.preview.configure(image='', text='Chưa có ảnh')
        if self.images:
            index = min(index, len(self.images) - 1)
            self.photo_list.selection_set(index)
            self.photo_list.see(index)
            self.show_photo()
        if self.on_photo_deleted is not None:
            self.on_photo_deleted(self.customer_id, image['id'])

    def rotate_photo(self):
        selected = self.photo_list.curselection()
        if not selected:
            return
        try:
            self.store.rotate_image(self.customer_id, self.images[selected[0]]['id'])
            self.show_photo()
            if self.on_photo_deleted is not None:
                owner = getattr(self.on_photo_deleted, '__self__', None)
                if owner is not None and getattr(owner, 'current_id', None) == self.customer_id:
                    owner.preview_photo()
        except Exception as exc:
            messagebox.showerror('Không thể xoay ảnh', str(exc), parent=self)

    def show_photo(self):
        selected = self.photo_list.curselection()
        if not selected:
            return
        try:
            with Image.open(self.store.image_path(self.images[selected[0]])) as source:
                image = ImageOps.exif_transpose(source)
                image.thumbnail((max(100, self.preview.winfo_width() - 10), max(100, self.preview.winfo_height() - 10)))
                self.preview_image = ImageTk.PhotoImage(image, master=self)
            self.preview.configure(image=self.preview_image, text='')
        except Exception:
            self.preview_image = None
            self.preview.configure(image='', text='Không đọc được ảnh đã lưu.')

    def print_photo(self):
        if not self.images:
            messagebox.showinfo('In ảnh', 'Khách hàng chưa có ảnh đã lưu để in.', parent=self)
            return
        try:
            from printing import open_print_preview
            sources = [self.store.image_path(image) for image in self.images]
            open_print_preview(sources, self.store.root / 'print-preview')
        except Exception as exc:
            messagebox.showerror('Không mở được bản in', str(exc), parent=self)

    def open_original(self):
        selected = self.photo_list.curselection()
        if selected:
            try:
                os.startfile(str(self.store.image_path(self.images[selected[0]]).resolve()))
            except OSError as exc:
                messagebox.showerror('Không mở được ảnh', str(exc), parent=self)

    def close(self):
        self.grab_release()
        self.destroy()
        if self.previous_focus is not None and self.previous_focus.winfo_exists():
            self.previous_focus.focus_set()
        else:
            self.parent.focus_set()


class App:
    def __init__(self, root, store, config_path=None):
        from layout import build_app
        self._scan_busy = False
        self._scan_after = None
        self._scan_revision = 0
        self.scan_source = None
        self.scan_preview_image = None
        self._scan_files = set()
        self._scan_directory = None
        self._pasted_files = set()
        self._paste_directory = None
        self.pending_rotations = {}
        self.config_path = Path(config_path) if config_path is not None else BASE / 'storage.json'
        build_app(self, root, store)

    def open_existing_storage(self):
        if not self.can_leave():
            return
        destination = filedialog.askdirectory(parent=self.root,
                title='Mở thư mục có customers.sqlite3 và images (hỗ trợ ổ mạng)',
                mustexist=True)
        if not destination:
            return
        if Path(destination).absolute() == self.store.root.absolute():
            self.status.set('Đây là nơi lưu dữ liệu hiện tại; không có thay đổi.')
            return
        if not messagebox.askyesno('Mở dữ liệu có sẵn',
                f'Dùng trực tiếp dữ liệu tại:\n{destination}\n\n'
                'Không sao chép, không ghi đè bằng dữ liệu hiện tại.\n'
                'SQLite qua SMB không bảo đảm an toàn khi nhiều máy cùng ghi. '
                'Không chỉnh sửa đồng thời; sao lưu thường xuyên và giữ kết nối mạng ổn định.\n\nTiếp tục?',
                icon='warning', default='no', parent=self.root):
            return
        try:
            from storage import open_existing
            replacement = open_existing(destination, self.config_path)
        except Exception as exc:
            messagebox.showerror('Không mở được dữ liệu có sẵn', str(exc), parent=self.root)
            return
        previous = self.store
        self.store = replacement
        previous.close()
        self.storage_path.set(str(self.store.root.absolute()))
        self.dirty = False
        self.new_customer()
        self.page = 1
        self.query.set('')
        self.refresh()
        self.status.set('Đã mở dữ liệu có sẵn • Không sửa đồng thời trên nhiều máy; nhớ sao lưu.')

    def choose_storage(self):
        if not self.can_leave():
            return
        destination = filedialog.askdirectory(parent=self.root, title='Chọn thư mục trống để lưu toàn bộ dữ liệu',
                                              initialdir=str(self.store.root.resolve().parent), mustexist=True)
        if not destination:
            return
        if Path(destination).resolve() == self.store.root.resolve():
            self.status.set('Đây là nơi lưu dữ liệu hiện tại; không có thay đổi.')
            return
        if not messagebox.askyesno('Xác nhận đổi nơi lưu dữ liệu',
                f'Sao chép toàn bộ khách hàng, ảnh và bản xem trước in đến:\n{destination}\n\n'
                'Thư mục đích phải trống. Dữ liệu cũ được giữ nguyên để sao lưu. '
                'Sau khi thành công, ứng dụng dùng nơi mới và ghi nhớ cho lần mở sau.\n\nTiếp tục?',
                default='no', parent=self.root):
            return
        try:
            from storage import relocate
            replacement = relocate(self.store, destination, self.config_path)
        except Exception as exc:
            messagebox.showerror('Không thể đổi nơi lưu', str(exc), parent=self.root)
            return
        previous = self.store
        self.store = replacement
        previous.close()
        self.storage_path.set(str(self.store.root.resolve()))
        self.dirty = False
        self.new_customer()
        self.refresh()
        self.status.set('Đã đổi nơi lưu dữ liệu. Bản dữ liệu cũ vẫn được giữ nguyên.')

    def mark_dirty(self, *args):
        self._scan_revision += 1
        if not self.loading:
            self.dirty = True

    def notes_changed(self, event=None):
        if self.notes.edit_modified():
            self.mark_dirty()
            self.notes.edit_modified(False)

    def can_leave(self):
        return not self.dirty or messagebox.askyesno('Chưa lưu thay đổi', 'Bỏ các thay đổi chưa lưu?', parent=self.root)

    def refresh(self):
        for frame in self.action_rows.values():
            frame.destroy()
        self.action_rows.clear()
        self.tree.delete(*self.tree.get_children())
        size = int(self.page_size.get())
        rows, total, self.page, self.total_pages = self.store.search_page(self.query.get(), self.page, size)
        self.tree.tag_configure('even', background='#ffffff')
        self.tree.tag_configure('odd', background='#f3f8fe')
        for index, row in enumerate(rows):
            self.tree.insert('', 'end', iid=row['id'], values=(row['name'], row['phone'], row['cccd']), tags=('even' if index % 2 == 0 else 'odd',))
            cid = row['id']
            from ui import RoundButton
            frame = tk.Frame(self.tree, bg='#ffffff' if index % 2 == 0 else '#f3f8fe')
            self.action_rows[cid] = frame
            for label, action, glyph, width in [('Chi tiết', self.show_details, 'eye', 76), ('Sửa', self.edit_customer, 'edit', 53), ('Xóa', self.delete_customer, 'delete', 53)]:
                button = RoundButton(frame, text=label, width=width, height=29,
                                     danger=label == 'Xóa', icon_name=glyph,
                                     command=lambda action=action, cid=cid: action(cid))
                button.pack(side='left', padx=2, pady=8)
        start = (self.page - 1) * size + 1 if total else 0
        end = (self.page - 1) * size + len(rows)
        self.count.configure(text=f'Hiển thị {start}–{end} / {total} khách hàng')
        self.page_label.configure(text=f'Trang {self.page} / {self.total_pages}')
        self.previous_button.state(['disabled'] if self.page <= 1 else ['!disabled'])
        self.next_button.state(['disabled'] if self.page >= self.total_pages else ['!disabled'])
        self.root.after_idle(self.position_actions)

    def reload_customers(self):
        """Load committed records from shared storage without touching the form."""
        try:
            # Query first so an unavailable share does not erase visible rows.
            self.store.search_page(self.query.get(), self.page, int(self.page_size.get()))
            self.refresh()
        except Exception as exc:
            messagebox.showerror('Không tải lại được dữ liệu', str(exc), parent=self.root)
            return
        self.status.set('Đã tải lại danh sách khách hàng.')

    def position_actions(self):
        for cid, frame in self.action_rows.items():
            box = self.tree.bbox(cid, 'actions')
            if box:
                x, y, width, height = box
                frame.place(x=x, y=y, width=width, height=height)
            else:
                frame.place_forget()

    def edit_customer(self, cid):
        if self.dirty and not self.can_leave():
            return
        self.load_customer(cid)
        self.tree.selection_set(cid)
        self.heading.configure(text='Sửa khách hàng')

    def show_details(self, cid):
        record, images = self.store.get(cid)
        if record is not None:
            self.detail_dialog = DetailDialog(self.root, self.store, record, images, self.photo_deleted)

    def photo_deleted(self, customer_id, image_id):
        if self.current_id == customer_id:
            selected = self.photos.curselection()
            self.saved_images = [image for image in self.saved_images if image['id'] != image_id]
            self.render_photos(selected[0] if selected else 0)

    def delete_customer(self, cid):
        record, images = self.store.get(cid)
        if record is None:
            return
        if not messagebox.askyesno('Xác nhận xóa khách hàng',
                f"Xóa khách hàng {record['name']}?\nSĐT: {record['phone']}\nCCCD: {record['cccd']}\n\n"
                f'Thông tin và {len(images)} ảnh đã lưu sẽ bị xóa vĩnh viễn. Không thể hoàn tác.',
                icon='warning', default='no', parent=self.root):
            return
        try:
            failed = self.store.delete(cid)
        except Exception as exc:
            messagebox.showerror('Không thể xóa', str(exc), parent=self.root)
            return
        if self.current_id == cid:
            self.dirty = False
            self.new_customer()
        self.refresh()
        self.status.set(f"Đã xóa khách hàng: {record['name']}")
        if failed:
            messagebox.showwarning('Chưa xóa hết tệp ảnh', 'Đã xóa hồ sơ nhưng các tệp sau vẫn còn trên ổ đĩa:\n' + '\n'.join(failed), parent=self.root)

    def move_page(self, delta):
        self.page = max(1, min(self.page + delta, self.total_pages))
        self.refresh()

    def change_page_size(self):
        self.page = 1
        self.refresh()

    def select_customer(self, event=None):
        selected = self.tree.selection()
        if selected and selected[0] != self.current_id:
            if self.can_leave():
                self.load_customer(selected[0])
            elif self.current_id and self.tree.exists(self.current_id):
                self.tree.selection_set(self.current_id)

    def new_customer(self):
        if not self.can_leave():
            return
        self.cleanup_pasted()
        self.clear_scan_photo()
        self.loading = True
        self.current_id = None
        for variable in (self.name, self.phone, self.cccd, self.address):
            variable.set('')
        self.notes.delete('1.0', 'end')
        self.notes.edit_modified(False)
        self.pending, self.saved_images = [], []
        self.pending_rotations.clear()
        self.render_photos()
        self.heading.configure(text='⊕  Tạo khách hàng mới')
        self.tree.selection_remove(*self.tree.selection())
        self.loading, self.dirty = False, False

    def load_customer(self, cid):
        record, images = self.store.get(cid)
        if record is None:
            return
        self.cleanup_pasted()
        self.clear_scan_photo()
        self.loading = True
        self.current_id = cid
        self.name.set(record['name'])
        self.phone.set(record['phone'])
        self.cccd.set(record['cccd'])
        self.address.set(record['address'])
        self.notes.delete('1.0', 'end')
        self.notes.insert('1.0', record['notes'])
        self.notes.edit_modified(False)
        self.saved_images, self.pending = list(images), []
        self.pending_rotations.clear()
        self.heading.configure(text='Thông tin khách hàng')
        self.render_photos()
        self.loading, self.dirty = False, False

    def save_customer(self):
        try:
            cid = self.store.save(self.current_id, self.name.get(), self.phone.get(), self.cccd.get(), self.notes.get('1.0', 'end-1c'), self.pending, address=self.address.get(), photo_rotations=self.pending_rotations)
        except Exception as exc:
            messagebox.showerror('Không thể lưu', str(exc), parent=self.root)
            return
        self.load_customer(cid)
        self.refresh()
        if self.tree.exists(cid):
            self.tree.selection_set(cid)
            self.tree.see(cid)
        self.status.set(f'Đã lưu: {self.name.get()} • {len(self.saved_images)} ảnh • {self.store.root.resolve()}')

    def cleanup_pasted(self, path=None):
        """Delete only temporary files created by this application instance."""
        targets = self._pasted_files.copy() if path is None else {path} & self._pasted_files
        failed = []
        for target in targets:
            try:
                target.unlink(missing_ok=True)
                self._pasted_files.discard(target)
            except OSError:
                failed.append(str(target))
        if self._paste_directory is not None and not self._pasted_files:
            try:
                self._paste_directory.rmdir()
                self._paste_directory = None
            except OSError:
                failed.append(str(self._paste_directory))
        if failed:
            messagebox.showwarning('Chưa dọn được ảnh tạm',
                'Không thể xóa các tệp tạm sau (có thể đang mở ở ứng dụng khác). '
                'Đóng ứng dụng đang giữ tệp rồi thử lại; nếu đã thoát SaveCCCD, hãy xóa thủ công:\n' + '\n'.join(failed), parent=self.root)

    def paste_photo(self, event=None):
        path = None
        created = False
        try:
            clipboard = ImageGrab.grabclipboard()
            if not isinstance(clipboard, Image.Image):
                messagebox.showinfo('Dán ảnh', 'Clipboard chưa có ảnh. Nhấn Win+Shift+S để chụp, rồi bấm Dán ảnh.\nẢnh có sẵn trên ổ đĩa: dùng Chọn ảnh.', parent=self.root)
                return 'break'
            if self._paste_directory is None:
                self._paste_directory = Path(tempfile.mkdtemp(prefix='SaveCCCD-paste-'))
            path = self._paste_directory / f'Anh-dan-{uuid.uuid4().hex}.png'
            with path.open('xb') as output:
                created = True
                self._pasted_files.add(path)
                clipboard.save(output, format='PNG')
        except Exception as exc:
            if created:
                self.cleanup_pasted(path)
            messagebox.showerror('Không thể dán ảnh', str(exc), parent=self.root)
            return 'break'
        self.pending.append(path)
        self.dirty = True
        self.render_photos(len(self.saved_images) + len(self.pending) - 1)
        self.status.set('Đã dán ảnh • Bấm Lưu khách hàng để lưu vào nơi đã chọn.')
        return 'break'

    def add_photos(self):
        paths = filedialog.askopenfilenames(parent=self.root, title='Chọn ảnh khách hàng / CCCD', filetypes=[('Ảnh', '*.jpg *.jpeg *.png *.webp *.bmp'), ('Tất cả', '*.*')])
        for item in paths:
            path = Path(item)
            if path not in self.pending:
                self.pending.append(path)
        if paths:
            self.dirty = True
            self.render_photos()

    def rotate_photo(self):
        selected = self.photos.curselection()
        if not selected:
            return
        index = selected[0]
        try:
            if index < len(self.saved_images):
                self.store.rotate_image(self.current_id, self.saved_images[index]['id'])
            else:
                path = self.pending[index - len(self.saved_images)]
                with Image.open(path) as source:
                    source.verify()
                self.pending_rotations[path] = (self.pending_rotations.get(path, 0) + 1) % 4
                self.dirty = True
            self.preview_photo()
            self.status.set('Đã xoay ảnh 90° sang phải' + (' • Bấm Lưu khách hàng để lưu.' if index >= len(self.saved_images) else ' • Đã lưu.'))
        except Exception as exc:
            messagebox.showerror('Không thể xoay ảnh', str(exc), parent=self.root)

    def delete_photo(self):
        selected = self.photos.curselection()
        if not selected:
            return
        index = selected[0]
        if index >= len(self.saved_images):
            path = self.pending.pop(index - len(self.saved_images))
            self.cleanup_pasted(path)
            self.pending_rotations.pop(path, None)
            self.dirty = True
        else:
            image = self.saved_images[index]
            if not confirm_photo_deletion(self.root, self.store, self.current_id, image):
                return
            self.saved_images.pop(index)
            self.status.set(f"Đã xóa ảnh: {image['original_name']}")
        self.render_photos(index)

    def remove_pending(self):
        selected = self.photos.curselection()
        if not selected:
            return
        index = selected[0] - len(self.saved_images)
        if index < 0:
            messagebox.showinfo('Ảnh đã lưu', 'Nút này chỉ bỏ ảnh mới chọn, không xóa ảnh đã lưu.', parent=self.root)
            return
        path = self.pending.pop(index)
        self.cleanup_pasted(path)
        self.pending_rotations.pop(path, None)
        self.dirty = True
        self.render_photos()

    def render_photos(self, selected_index=0):
        self.photos.delete(0, 'end')
        for image in self.saved_images:
            self.photos.insert('end', image['original_name'])
        for path in self.pending:
            self.photos.insert('end', '[Chưa lưu] ' + path.name)
        self.photo_count.configure(text=f'Ảnh khách hàng ({len(self.saved_images)} đã lưu, {len(self.pending)} chưa lưu)')
        self.preview_image = None
        self.preview.configure(image='', text='Ảnh xem trước')
        if self.photos.size():
            index = min(selected_index, self.photos.size() - 1)
            self.photos.selection_set(index)
            self.photos.see(index)
            self.preview_photo()

    def selected_photo(self):
        selected = self.photos.curselection()
        if not selected:
            return None
        index = selected[0]
        return self.store.image_path(self.saved_images[index]) if index < len(self.saved_images) else self.pending[index - len(self.saved_images)]

    def cleanup_scan_files(self):
        """Remove only owned scan copies, never the user's original file."""
        failed = False
        for path in self._scan_files.copy():
            if path == self.scan_source:
                continue
            try:
                path.unlink(missing_ok=True)
                self._scan_files.discard(path)
            except OSError:
                failed = True
        if self._scan_directory is not None and not self._scan_files:
            try:
                self._scan_directory.rmdir()
                self._scan_directory = None
            except OSError:
                failed = True
        if failed:
            messagebox.showwarning('Chưa dọn được ảnh quét tạm',
                'Ảnh tạm đang bị khóa. Đóng ứng dụng giữ tệp rồi thử Xóa ảnh quét lần nữa. '
                'Thư mục tạm: ' + str(self._scan_directory), parent=self.root)

    def clear_scan_photo(self):
        self._scan_revision += 1
        self.scan_source = None
        self.scan_preview_image = None
        self.scan_preview.configure(image='', text='Một ảnh QR để quét\nKhông lưu / không in')
        self.cleanup_scan_files()

    def set_scan_image(self, source):
        """Stage one validated image separately from customer attachments."""
        path = None
        try:
            if isinstance(source, Image.Image):
                image = ImageOps.exif_transpose(source)
            else:
                with Image.open(source) as original:
                    if original.width * original.height > 24_000_000:
                        raise ValueError('Ảnh vượt 24 triệu điểm ảnh.')
                    image = ImageOps.exif_transpose(original)
            if image.width * image.height > 24_000_000:
                raise ValueError('Ảnh vượt 24 triệu điểm ảnh.')
            if self._scan_directory is None:
                self._scan_directory = Path(tempfile.mkdtemp(prefix='SaveCCCD-scan-'))
            candidate = self._scan_directory / (uuid.uuid4().hex + '.png')
            with candidate.open('xb') as output:
                path = candidate
                self._scan_files.add(path)
                image.save(output, format='PNG')
            preview = image.copy()
            preview.thumbnail((110, 78))
            preview_image = ImageTk.PhotoImage(preview, master=self.root)
        except Exception:
            self.cleanup_scan_files()
            messagebox.showerror('Không thể chọn ảnh quét',
                'Không đọc hoặc tạo được ảnh quét (tối đa 24 triệu điểm ảnh). Ảnh trước được giữ nguyên.', parent=self.root)
            return
        self._scan_revision += 1
        self.scan_source = path
        self.scan_preview_image = preview_image
        self.scan_preview.configure(image=preview_image, text='')
        self.cleanup_scan_files()
        self.status.set('Ảnh quét riêng • Không lưu vào hồ sơ, không đưa vào bản in.')

    def choose_scan_photo(self):
        path = filedialog.askopenfilename(parent=self.root, title='Chọn một ảnh để quét CCCD (không lưu)',
                filetypes=[('Ảnh', '*.jpg *.jpeg *.png *.webp *.bmp'), ('Tất cả', '*.*')])
        if path:
            self.set_scan_image(path)

    def paste_scan_photo(self, event=None):
        try:
            image = ImageGrab.grabclipboard()
        except Exception:
            messagebox.showerror('Không thể dán ảnh quét', 'Không đọc được clipboard. Hãy thử lại.', parent=self.root)
            return 'break'
        if not isinstance(image, Image.Image):
            messagebox.showinfo('Dán ảnh quét', 'Clipboard chưa có ảnh. Nhấn Win+Shift+S rồi Dán ảnh trong vùng quét.', parent=self.root)
            return 'break'
        self.set_scan_image(image)
        return 'break'

    def scan_photo(self):
        """Decode the separate scan input off Tk; apply only to unchanged drafts."""
        if self._scan_busy:
            return
        path = self.scan_source
        if path is None:
            messagebox.showinfo('Quét thông tin CCCD', 'Chọn hoặc dán một ảnh trong vùng Quét thông tin CCCD riêng.', parent=self.root)
            return
        import queue
        import threading
        from cccd_qr import scan_cccd, ScanError
        def snapshot():
            return (self._scan_revision, id(self.store), self.current_id,
                    self.scan_source, self.name.get(), self.cccd.get(),
                    self.phone.get(), self.address.get(), self.notes.get('1.0', 'end-1c'))
        before = snapshot()
        result = queue.Queue(maxsize=1)
        self._scan_busy = True
        self.scan_photo_button.state(['disabled'])
        self.scan_photo_button.configure(text='Đang quét QR…')
        self.status.set('Đang quét mã QR cục bộ; không gửi ảnh lên mạng.')
        def work():
            try:
                result.put((scan_cccd(path), None))
            except ScanError as exc:
                result.put((None, str(exc)))
            except ImportError:
                result.put((None, 'Thiếu thư viện quét QR. Đóng và mở lại bằng MoUngDung.bat để cài thư viện.'))
            except Exception:
                result.put((None, 'Không thể quét ảnh. Hãy thử ảnh rõ hơn.'))
        def poll():
            self._scan_after = None
            try:
                identity, error = result.get_nowait()
            except queue.Empty:
                self._scan_after = self.root.after(50, poll)
                return
            self._scan_busy = False
            self.scan_photo_button.state(['!disabled'])
            self.scan_photo_button.configure(text='Quét')
            if before != snapshot():
                self.status.set('Đã bỏ kết quả QR vì ảnh hoặc thông tin đang sửa đã thay đổi. Hãy quét lại.')
                return
            if error:
                self.status.set('Chưa điền thông tin CCCD từ QR.')
                messagebox.showerror('Không thể quét CCCD', error, parent=self.root)
                return
            name, cccd, address = identity
            if ((self.name.get().strip() and self.name.get() != name)
                    or (self.cccd.get().strip() and self.cccd.get() != cccd)
                    or (address.strip() and self.address.get().strip() and self.address.get() != address)):
                if not messagebox.askyesno('Thay thông tin từ QR?',
                        'Tên, CCCD hoặc địa chỉ hiện tại khác với QR. Thay bằng thông tin đọc từ QR?\n'
                        'Các thông tin và ảnh khác được giữ nguyên. Chưa lưu tự động.',
                        default='no', parent=self.root):
                    self.status.set('Đã hủy điền thông tin từ QR; dữ liệu giữ nguyên.')
                    return
            self.name.set(name)
            self.cccd.set(cccd)
            if address.strip():
                self.address.set(address)
            self.dirty = True
            self.form_canvas.yview_moveto(0)
            self.status.set('Đã điền thông tin từ QR (địa chỉ nếu có). Kiểm tra lại rồi bấm Lưu; đây không phải xác thực danh tính.')
        threading.Thread(target=work, daemon=True, name='local-cccd-qr').start()
        self._scan_after = self.root.after(50, poll)

    def preview_photo(self):
        path = self.selected_photo()
        if path is None:
            return
        try:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source)
                selected = self.photos.curselection()
                if selected and selected[0] >= len(self.saved_images):
                    turns = self.pending_rotations.get(path, 0) % 4
                    if turns:
                        image = image.transpose((Image.Transpose.ROTATE_270, Image.Transpose.ROTATE_180,
                                                 Image.Transpose.ROTATE_90)[turns - 1])
                image.thumbnail((98, 78))
                self.preview_image = ImageTk.PhotoImage(image, master=self.root)
            self.preview.configure(image=self.preview_image, text='')
        except Exception:
            self.preview_image = None
            self.preview.configure(image='', text='Không đọc được ảnh. Hãy kiểm tra tệp đã chọn.')

    def open_photo(self):
        path = self.selected_photo()
        if path:
            try:
                os.startfile(str(path.resolve()))
            except OSError as exc:
                messagebox.showerror('Không mở được ảnh', str(exc), parent=self.root)

    def close_window(self):
        if self.can_leave():
            if self._scan_after is not None:
                self.root.after_cancel(self._scan_after)
                self._scan_after = None
            self.cleanup_pasted()
            self.clear_scan_photo()
            self.root.destroy()


def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    try:
        from storage import open_store
        store = open_store(BASE)
    except Exception as exc:
        messagebox.showerror('Không mở được dữ liệu', str(exc), parent=root)
        root.destroy()
        return
    app = None
    try:
        app = App(root, store)
        root.mainloop()
    finally:
        (app.store if app is not None else store).close()


if __name__ == '__main__':
    main()
