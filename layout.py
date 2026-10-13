"""Blue-white customer workspace; pinned actions and scrollable form."""
import tkinter as tk
from tkinter import ttk
from ui import RoundedPanel, RoundButton, RoundEntry, ImageChooser, label, icon, PAGE, BLUE, NAVY, LINE


def section(master, text, kind):
    bar=tk.Frame(master,bg='#eaf3ff',height=46)
    bar.pack(fill='x');bar.pack_propagate(False)
    glyph=icon(bar,kind,23)
    badge=tk.Label(bar,image=glyph,bg='#eaf3ff');badge.image=glyph;badge.pack(side='left',padx=(15,9))
    heading=label(bar,text,bold=True,size=17);heading.pack(side='left')
    return heading


def build_app(app,root,store):
    app.root,app.store=root,store
    app.current_id=None;app.pending=[];app.saved_images=[];app.preview_image=None
    app.dirty=False;app.loading=False;app.action_rows={}
    root.title('SaveCCCD • Quản lý khách hàng');root.geometry('1250x800');root.minsize(1000,580);root.configure(bg=PAGE)
    style=ttk.Style(root);style.theme_use('clam')
    style.configure('.',font=('Segoe UI',-13))
    style.configure('Treeview',rowheight=46,font=('Segoe UI',-13),background='white',fieldbackground='white',foreground=NAVY,borderwidth=0)
    style.configure('Treeview.Heading',font=('Segoe UI',-13,'bold'),padding=(5,12),background='#eaf3ff',foreground=NAVY,relief='flat')
    style.map('Treeview',background=[('selected','#dfeeff')],foreground=[('selected',NAVY)])
    style.configure('Accent.TButton',background=BLUE)
    style.configure('Vertical.TScrollbar',background='#dbe7f4',troughcolor='#f7faff',borderwidth=0,arrowsize=12)
    header=tk.Frame(root,bg=PAGE,height=96);header.pack(fill='x');header.pack_propagate(False)
    tile=RoundedPanel(header,radius=13,fill=BLUE,border=BLUE,width=55,height=55);tile.pack(side='left',padx=(22,14),pady=19)
    glyph=icon(tile.content,'people',38,'white');badge=tk.Label(tile.content,image=glyph,bg=BLUE);badge.image=glyph;badge.pack()
    titles=tk.Frame(header,bg=PAGE);titles.pack(side='left')
    label(titles,'Hồ sơ khách hàng',bold=True,size=29).pack(anchor='w')
    label(titles,'Lưu ảnh tại máy • Tra cứu nhanh theo tên, số điện thoại và CCCD',muted=True,size=13).pack(anchor='w',pady=(5,0))
    app.status=tk.StringVar(value=f'Dữ liệu lưu tại: {store.root.resolve()}')
    storage_footer=tk.Frame(root,bg=PAGE);storage_footer.pack(side='bottom',fill='x',padx=23,pady=(6,8))
    app.storage_button=RoundButton(storage_footer,'Chuyển dữ liệu…',app.choose_storage,width=145,height=36)
    app.storage_button.pack(side='right',padx=(8,0))
    app.open_storage_button=RoundButton(storage_footer,'Mở dữ liệu có sẵn',app.open_existing_storage,width=169,height=36)
    app.open_storage_button.pack(side='right',padx=(8,0))
    storage_info=tk.Frame(storage_footer,bg=PAGE);storage_info.pack(side='left',fill='x',expand=True)
    path_row=tk.Frame(storage_info,bg=PAGE);path_row.pack(fill='x')
    label(path_row,'Nơi lưu:',muted=True,size=12).pack(side='left',padx=(0,6))
    app.storage_path=tk.StringVar(value=str(store.root.resolve()))
    app.storage_path_entry=tk.Entry(path_row,textvariable=app.storage_path,state='readonly',readonlybackground=PAGE,
                                    relief='flat',bd=0,fg=NAVY,font=('Segoe UI',-12))
    app.storage_path_entry.pack(side='left',fill='x',expand=True)
    label(storage_info,textvariable=app.status,muted=True,size=11,anchor='w').pack(fill='x')
    body=tk.Frame(root,bg=PAGE);body.pack(fill='both',expand=True,padx=20)
    body.columnconfigure(0,weight=61,uniform='cards');body.columnconfigure(1,weight=39,uniform='cards');body.rowconfigure(0,weight=1)
    app.left_card=RoundedPanel(body,radius=15);app.left_card.grid(row=0,column=0,sticky='nsew',padx=(0,8))
    app.right_card=RoundedPanel(body,radius=15);app.right_card.grid(row=0,column=1,sticky='nsew',padx=(8,0))
    left=app.left_card.content;right=app.right_card.content
    section(left,'Tìm khách hàng','search')
    section_heading=section(right,'Tạo khách hàng mới','plus');app.heading=section_heading
    app.query=tk.StringVar();app.page=1;app.total_pages=1;app.page_size=tk.StringVar(value='20')
    search_row=tk.Frame(left,bg='white');search_row.pack(fill='x',padx=15,pady=(16,8))
    app.search_button=RoundButton(search_row,'Tìm kiếm',app.change_page_size,primary=True,icon_name='search',width=110)
    app.search_button.pack(side='right',padx=(8,0))
    search=RoundEntry(search_row,app.query,'Nhập tên, SĐT hoặc CCCD…','search',height=36);search.pack(fill='x',expand=True)
    search.entry.bind('<Return>',lambda e:app.change_page_size())
    label(left,'Tìm theo một phần tên, có hoặc không dấu',muted=True,size=12).pack(anchor='w',padx=17,pady=(0,12))
    footer=tk.Frame(left,bg='white');footer.pack(side='bottom',fill='x',padx=15,pady=(10,2))
    count_row=tk.Frame(footer,bg='white');count_row.pack(fill='x',pady=(0,10))
    app.count=label(count_row,muted=True,size=12);app.count.pack(side='left')
    RoundButton(count_row,'Tạo khách hàng mới',app.new_customer,width=177,icon_name='plus',height=29).pack(side='right')
    pager=tk.Frame(footer,bg='white');pager.pack(fill='x')
    app.previous_button=RoundButton(pager,'‹ Trước',lambda:app.move_page(-1),width=75,height=33);app.previous_button.pack(side='left')
    app.page_label=label(pager,'Trang 1 / 1',size=12,padx=9);app.page_label.pack(side='left')
    app.next_button=RoundButton(pager,'Sau ›',lambda:app.move_page(1),width=65,height=33);app.next_button.pack(side='left')
    picker=ttk.Combobox(pager,textvariable=app.page_size,values=('20','50','100'),state='readonly',width=4);picker.pack(side='right');picker.bind('<<ComboboxSelected>>',lambda e:app.change_page_size())
    label(pager,'Số dòng: ',size=12).pack(side='right')
    table=tk.Frame(left,bg='white');table.pack(fill='both',expand=True,padx=15)
    app.tree=ttk.Treeview(table,columns=('name','phone','cccd','actions'),show='headings',selectmode='browse',height=7)
    for key,title,width in [('name','Tên khách hàng',155),('phone','Số điện thoại',102),('cccd','CCCD',117),('actions','Thao tác',194)]:
        app.tree.heading(key,text=title);app.tree.column(key,width=width,minwidth=65 if key=='name' else width,stretch=key=='name',anchor='w' if key=='name' else 'center')
    scrollbar=ttk.Scrollbar(table,orient='vertical',command=app.tree.yview)
    scrollbar.pack(side='right',fill='y');app.tree.pack(fill='both',expand=True)
    def scrolled(a,b):scrollbar.set(a,b);app.position_actions()
    app.tree.configure(yscrollcommand=scrolled)
    def fit_table(event=None):
        available=app.tree.winfo_width()-2
        fixed=102+117+194
        app.tree.column('name',width=max(65,available-fixed),stretch=False)
        app.tree.column('phone',width=102,stretch=False)
        app.tree.column('cccd',width=117,stretch=False)
        app.tree.column('actions',width=194,stretch=False)
        app.position_actions()
    app.tree.bind('<Configure>',fit_table);app.tree.bind('<ButtonRelease-1>',fit_table)
    # Footer gets space before the scrolling content, so Save can never disappear.
    save_footer=tk.Frame(right,bg='white');save_footer.pack(side='bottom',fill='x',padx=16,pady=(12,2))
    app.save_button=RoundButton(save_footer,'Lưu khách hàng',app.save_customer,primary=True,icon_name='save',height=42)
    app.save_button.pack(fill='x')
    scroll_area=tk.Frame(right,bg='white');scroll_area.pack(fill='both',expand=True,padx=(15,7),pady=(12,0))
    app.form_canvas=tk.Canvas(scroll_area,bg='white',highlightthickness=0,bd=0)
    app.form_scrollbar=ttk.Scrollbar(scroll_area,orient='vertical',command=app.form_canvas.yview)
    app.form_scrollbar.pack(side='right',fill='y');app.form_canvas.pack(side='left',fill='both',expand=True)
    app.form_canvas.configure(yscrollcommand=app.form_scrollbar.set)
    form=tk.Frame(app.form_canvas,bg='white');window=app.form_canvas.create_window(0,0,window=form,anchor='nw')
    form.bind('<Configure>',lambda e:app.form_canvas.configure(scrollregion=app.form_canvas.bbox('all')))
    app.form_canvas.bind('<Configure>',lambda e:app.form_canvas.itemconfigure(window,width=e.width))
    app.name,app.phone,app.cccd,app.address=tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar()
    for text,var,placeholder,kind in [('Tên khách hàng *',app.name,'Nhập tên khách hàng…','user'),('Số điện thoại',app.phone,'Nhập số điện thoại…','phone'),('Số CCCD (12 chữ số)',app.cccd,'Nhập số CCCD (12 chữ số)…','id'),('Địa chỉ',app.address,'Nhập địa chỉ…',None)]:
        label(form,text,bold=True).pack(anchor='w',pady=(0,5))
        field=RoundEntry(form,var,placeholder,kind);field.pack(fill='x',pady=(0,7));var.trace_add('write',app.mark_dirty)
    label(form,'Ghi chú',bold=True).pack(anchor='w',pady=(0,5))
    note_panel=RoundedPanel(form,radius=7,height=57,padding=9);note_panel.pack(fill='x',pady=(0,7))
    app.notes=tk.Text(note_panel.content,font=('Segoe UI',-13),relief='flat',bd=0,wrap='word',fg=NAVY,background='white',height=2)
    app.notes.pack(fill='both',expand=True);app.notes.bind('<<Modified>>',app.notes_changed)
    app.scan_panel=RoundedPanel(form,radius=9,height=212,padding=10,fill='#f7faff')
    app.scan_panel.pack(fill='x',pady=(2,12))
    scan=app.scan_panel.content
    label(scan,'Quét thông tin CCCD',bold=True,size=14).pack(anchor='w',pady=(0,4))
    label(scan,'Ảnh riêng • Không lưu vào hồ sơ / không in',muted=True,size=11).pack(anchor='w')
    scan_row=tk.Frame(scan,bg='#f7faff');scan_row.pack(fill='x',pady=7)
    scan_thumbnail=tk.Frame(scan_row,bg='#eaf3ff',width=122,height=84)
    scan_thumbnail.pack(side='right',padx=(8,0));scan_thumbnail.pack_propagate(False)
    app.scan_preview=tk.Label(scan_thumbnail,text='Một ảnh QR để quét\nKhông lưu / không in',bg='#eaf3ff',fg=NAVY,
                              font=('Segoe UI',-11),takefocus=1)
    app.scan_preview.pack(fill='both',expand=True)
    scan_actions=tk.Frame(scan_row,bg='#f7faff');scan_actions.pack(side='left',fill='x',expand=True)
    app.choose_scan_button=RoundButton(scan_actions,'Chọn ảnh',app.choose_scan_photo,height=32)
    app.choose_scan_button.pack(fill='x',pady=(0,5))
    app.paste_scan_button=RoundButton(scan_actions,'Dán ảnh',app.paste_scan_photo,height=32)
    app.paste_scan_button.pack(fill='x')
    scan_bottom=tk.Frame(scan,bg='#f7faff');scan_bottom.pack(fill='x')
    app.clear_scan_button=RoundButton(scan_bottom,'Xóa ảnh quét',app.clear_scan_photo,width=120,height=32)
    app.clear_scan_button.pack(side='right',padx=(7,0))
    app.scan_photo_button=RoundButton(scan_bottom,'Quét',app.scan_photo,height=32,primary=True,icon_name='id')
    app.scan_photo_button.pack(side='left',fill='x',expand=True)
    for target in (app.scan_preview, app.choose_scan_button, app.paste_scan_button, app.clear_scan_button, app.scan_photo_button):
        target.bind('<Control-v>',app.paste_scan_photo)
        target.bind('<Control-V>',app.paste_scan_photo)
        target.bind('<ButtonPress-1>',lambda e:e.widget.focus_set())
    app.photo_count=label(form,'Ảnh khách hàng (0 đã lưu, 0 chưa lưu)',bold=True)
    app.photo_count.pack(anchor='w',pady=(0,7))
    photo_row=tk.Frame(form,bg='white',height=106);photo_row.pack(fill='x');photo_row.pack_propagate(False)
    thumbnail=RoundedPanel(photo_row,radius=8,width=111,height=106,fill='#f7faff');thumbnail.pack(side='right',padx=(10,0))
    app.preview=tk.Label(thumbnail.content,text='Ảnh xem trước',font=('Segoe UI',-11),fg='#8398ae',bg='#f7faff',wraplength=92)
    app.preview.pack(fill='both',expand=True)
    app.image_chooser=ImageChooser(photo_row,app.add_photos)
    app.image_chooser.pack(fill='both',expand=True)
    app.photos=tk.Listbox(form,height=2,font=('Segoe UI',-12),exportselection=False,relief='flat',bd=0,highlightthickness=1,highlightbackground=LINE,selectbackground='#dfeeff',selectforeground=NAVY)
    app.photos.pack(fill='x',pady=(9,7));app.photos.bind('<<ListboxSelect>>',lambda e:app.preview_photo());app.photos.bind('<Double-1>',lambda e:app.open_photo())
    photo_actions=tk.Frame(form,bg='white');photo_actions.pack(fill='x')
    app.paste_photo_button=RoundButton(photo_actions,'Dán ảnh',app.paste_photo,width=100,height=29)
    app.paste_photo_button.pack(side='left',padx=(0,8))
    app.delete_photo_button=RoundButton(photo_actions,'Xóa ảnh đã chọn',app.delete_photo,width=165,height=29,danger=True,icon_name='delete')
    app.delete_photo_button.pack(side='left')

    # No root binding: entry and notes keep their normal text paste behavior.
    for target in (app.image_chooser, app.preview, app.photos, app.paste_photo_button, app.delete_photo_button):
        target.bind('<Control-v>',app.paste_photo)
        target.bind('<Control-V>',app.paste_photo)
    app.preview.configure(takefocus=1)
    app.preview.bind('<Button-1>',lambda e:app.preview.focus_set())
    app.image_chooser.bind('<Button-1>',lambda e:app.image_chooser.focus_set())
    def wheel(event):
        target=event.widget
        while target is not None:
            if target is scroll_area:
                if app.form_canvas.bbox('all')[3]>app.form_canvas.winfo_height():app.form_canvas.yview_scroll(-1 if event.delta>0 else 1,'units')
                return 'break'
            target=getattr(target,'master',None)
    # Root binding catches descendants including entries, listboxes and thumbnails.
    root.bind('<MouseWheel>',wheel,add='+')
    app.query.trace_add('write',lambda *args:app.change_page_size())
    app.tree.bind('<<TreeviewSelect>>',app.select_customer)
    root.protocol('WM_DELETE_WINDOW',app.close_window);root.bind('<Control-s>',lambda e:app.save_customer());root.bind('<Control-f>',lambda e:search.entry.focus_set())
    app.refresh()
