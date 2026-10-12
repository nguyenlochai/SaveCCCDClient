"""Quản lý khách hàng cục bộ. Chạy: python app.py"""
from pathlib import Path
import sqlite3
import unicodedata
import uuid
import shutil
from PIL import Image

BASE = Path(__file__).resolve().parent


def normalize(value):
    value = value.lower().replace('đ', 'd')
    return ''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.combining(c))


class Store:
    def __init__(self, directory):
        self.root = Path(directory)
        (self.root / 'images').mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / 'customers.sqlite3')
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL,
                cccd TEXT NOT NULL, notes TEXT NOT NULL, search_text TEXT NOT NULL,
                updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
                filename TEXT NOT NULL, original_name TEXT NOT NULL);
        ''')

    def save(self, customer_id, name, phone, cccd, notes, photos=()):
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
                self.db.execute('''INSERT INTO customers(id,name,phone,cccd,notes,search_text)
                    VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,phone=excluded.phone,cccd=excluded.cccd,
                    notes=excluded.notes,search_text=excluded.search_text,updated=CURRENT_TIMESTAMP''',
                    (customer_id, name, phone, cccd, notes, normalize(f'{name} {phone} {cccd}')))
                for source in photos:
                    source = Path(source)
                    with Image.open(source) as image:
                        image.verify()
                    image_id = uuid.uuid4().hex
                    filename = image_id + source.suffix.lower()
                    target = self.root / 'images' / filename
                    copied.append(target)
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


class DetailDialog(tk.Toplevel):
    def __init__(self, parent, store, record, images):
        super().__init__(parent)
        from detail_layout import build_detail
        build_detail(self, parent, store, record, images)

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
        selected = self.photo_list.curselection()
        if not selected:
            messagebox.showinfo('In ảnh', 'Vui lòng chọn một ảnh đã lưu để in.', parent=self)
            return
        try:
            from printing import open_print_preview
            open_print_preview(self.store.image_path(self.images[selected[0]]), self.store.root / 'print-preview')
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
        self.config_path = Path(config_path) if config_path is not None else BASE / 'storage.json'
        build_app(self, root, store)

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
            self.detail_dialog = DetailDialog(self.root, self.store, record, images)

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
        self.loading = True
        self.current_id = None
        for variable in (self.name, self.phone, self.cccd):
            variable.set('')
        self.notes.delete('1.0', 'end')
        self.notes.edit_modified(False)
        self.pending, self.saved_images = [], []
        self.render_photos()
        self.heading.configure(text='⊕  Tạo khách hàng mới')
        self.tree.selection_remove(*self.tree.selection())
        self.loading, self.dirty = False, False

    def load_customer(self, cid):
        record, images = self.store.get(cid)
        if record is None:
            return
        self.loading = True
        self.current_id = cid
        self.name.set(record['name'])
        self.phone.set(record['phone'])
        self.cccd.set(record['cccd'])
        self.notes.delete('1.0', 'end')
        self.notes.insert('1.0', record['notes'])
        self.notes.edit_modified(False)
        self.saved_images, self.pending = list(images), []
        self.heading.configure(text='Thông tin khách hàng')
        self.render_photos()
        self.loading, self.dirty = False, False

    def save_customer(self):
        try:
            cid = self.store.save(self.current_id, self.name.get(), self.phone.get(), self.cccd.get(), self.notes.get('1.0', 'end-1c'), self.pending)
        except Exception as exc:
            messagebox.showerror('Không thể lưu', str(exc), parent=self.root)
            return
        self.load_customer(cid)
        self.refresh()
        if self.tree.exists(cid):
            self.tree.selection_set(cid)
            self.tree.see(cid)
        self.status.set(f'Đã lưu: {self.name.get()} • {len(self.saved_images)} ảnh • {self.store.root.resolve()}')

    def add_photos(self):
        paths = filedialog.askopenfilenames(parent=self.root, title='Chọn ảnh khách hàng / CCCD', filetypes=[('Ảnh', '*.jpg *.jpeg *.png *.webp *.bmp'), ('Tất cả', '*.*')])
        for item in paths:
            path = Path(item)
            if path not in self.pending:
                self.pending.append(path)
        if paths:
            self.dirty = True
            self.render_photos()

    def remove_pending(self):
        selected = self.photos.curselection()
        if not selected:
            return
        index = selected[0] - len(self.saved_images)
        if index < 0:
            messagebox.showinfo('Ảnh đã lưu', 'Nút này chỉ bỏ ảnh mới chọn, không xóa ảnh đã lưu.', parent=self.root)
            return
        self.pending.pop(index)
        self.dirty = True
        self.render_photos()

    def render_photos(self):
        self.photos.delete(0, 'end')
        for image in self.saved_images:
            self.photos.insert('end', image['original_name'])
        for path in self.pending:
            self.photos.insert('end', '[Chưa lưu] ' + path.name)
        self.preview_image = None
        self.preview.configure(image='', text='Ảnh xem trước')
        if self.photos.size():
            self.photos.selection_set(0)
            self.preview_photo()

    def selected_photo(self):
        selected = self.photos.curselection()
        if not selected:
            return None
        index = selected[0]
        return self.store.image_path(self.saved_images[index]) if index < len(self.saved_images) else self.pending[index - len(self.saved_images)]

    def preview_photo(self):
        path = self.selected_photo()
        if path is None:
            return
        try:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source)
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
