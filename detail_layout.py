"""Customer details with fitted attachment gallery and explicit deletion."""
import tkinter as tk
from tkinter import ttk
from ui import RoundedPanel, RoundButton, RoundEntry, label, icon, PAGE, LINE, NAVY


def build_detail(dialog,parent,store,record,images):
    dialog.parent,dialog.store,dialog.images=parent,store,list(images)
    dialog.preview_image=None;dialog.previous_focus=parent.focus_get();dialog.fields={}
    dialog.title('Chi tiết khách hàng');dialog.transient(parent);dialog.configure(bg=PAGE)
    dialog.geometry('640x660');dialog.minsize(600,610)
    dialog.card=RoundedPanel(dialog,radius=16);dialog.card.pack(fill='both',expand=True,padx=8,pady=8)
    content=dialog.card.content
    heading=tk.Frame(content,bg='white');heading.pack(fill='x',padx=20,pady=(4,17))
    glyph=icon(heading,'user',37);badge=tk.Label(heading,image=glyph,bg='#edf5ff',padx=8,pady=8);badge.image=glyph;badge.pack(side='left',padx=(0,12))
    title=tk.Frame(heading,bg='white');title.pack(side='left')
    label(title,'Chi tiết khách hàng',bold=True,size=23).pack(anchor='w')
    label(title,'Thông tin chi tiết và ảnh đã lưu',muted=True,size=12).pack(anchor='w',pady=(4,0))
    footer=tk.Frame(content,bg='white');footer.pack(side='bottom',fill='x',padx=20,pady=(13,3))
    RoundButton(footer,'Mở ảnh gốc',dialog.open_original,icon_name='open',width=140).pack(side='left')
    dialog.print_button=RoundButton(footer,'In ảnh',dialog.print_photo,width=100)
    dialog.print_button.pack(side='left',padx=(8,0))
    dialog.delete_photo_button=RoundButton(footer,'Xóa ảnh đã chọn',dialog.delete_photo,width=160,danger=True,icon_name='delete')
    dialog.delete_photo_button.pack(side='left',padx=(8,0))
    dialog.close_button=RoundButton(footer,'Đóng',dialog.close,primary=True,width=100,style='Accent.TButton');dialog.close_button.pack(side='right')
    info=tk.Frame(content,bg='white');info.pack(fill='x',padx=20);info.columnconfigure(1,weight=1)
    for i,(key,text) in enumerate([('name','Tên khách hàng'),('phone','Số điện thoại'),('cccd','CCCD'),('id','Mã hồ sơ'),('updated','Cập nhật (UTC)')]):
        label(info,text,bold=True,size=12).grid(row=i,column=0,sticky='w',padx=(0,16))
        var=tk.StringVar(master=dialog,value=record[key]);dialog.fields[key]=var
        RoundEntry(info,var,readonly=True,height=33).grid(row=i,column=1,sticky='ew',pady=3)
    label(info,'Địa chỉ đầy đủ',bold=True,size=12).grid(row=5,column=0,sticky='nw',pady=(10,0))
    address_panel=RoundedPanel(info,radius=7,fill='#f7faff',height=70,padding=9);address_panel.grid(row=5,column=1,sticky='ew',pady=(6,0))
    dialog.address=tk.Text(address_panel.content,height=2,font=('Segoe UI',-13),wrap='word',relief='flat',bd=0,bg='#f7faff',fg=NAVY)
    address_scroll=ttk.Scrollbar(address_panel.content,command=dialog.address.yview);address_scroll.pack(side='right',fill='y');dialog.address.configure(yscrollcommand=address_scroll.set)
    dialog.address.pack(fill='both',expand=True);dialog.address.insert('1.0',record['address']);dialog.address.configure(state='disabled')
    label(info,'Ghi chú đầy đủ',bold=True,size=12).grid(row=6,column=0,sticky='nw',pady=(10,0))
    notes_panel=RoundedPanel(info,radius=7,fill='#f7faff',height=70,padding=9);notes_panel.grid(row=6,column=1,sticky='ew',pady=(6,0))
    dialog.notes=tk.Text(notes_panel.content,height=2,font=('Segoe UI',-13),wrap='word',relief='flat',bd=0,bg='#f7faff',fg=NAVY)
    note_scroll=ttk.Scrollbar(notes_panel.content,command=dialog.notes.yview);note_scroll.pack(side='right',fill='y');dialog.notes.configure(yscrollcommand=note_scroll.set)
    dialog.notes.pack(fill='both',expand=True);dialog.notes.insert('1.0',record['notes']);dialog.notes.configure(state='disabled')
    gallery_title=tk.Frame(content,bg='white');gallery_title.pack(fill='x',padx=20,pady=(17,8))
    dialog.photo_count=label(gallery_title,f'Ảnh đã lưu ({len(images)})',bold=True,size=14)
    dialog.photo_count.pack(side='left')
    dialog.rotate_photo_button=RoundButton(gallery_title,'Xoay 90° ↻',dialog.rotate_photo,width=105,height=29)
    dialog.rotate_photo_button.pack(side='right')
    gallery=tk.Frame(content,bg='white');gallery.pack(fill='both',expand=True,padx=20)
    listing=RoundedPanel(gallery,radius=9,width=215,padding=6);listing.pack(side='left',fill='y',padx=(0,12))
    dialog.photo_list=tk.Listbox(listing.content,exportselection=False,font=('Segoe UI',-12),relief='flat',bd=0,highlightthickness=0,selectbackground='#dfeeff',selectforeground=NAVY,activestyle='none')
    photo_scroll=ttk.Scrollbar(listing.content,command=dialog.photo_list.yview);photo_scroll.pack(side='right',fill='y');dialog.photo_list.configure(yscrollcommand=photo_scroll.set);dialog.photo_list.pack(fill='both',expand=True)
    for i,image in enumerate(images,1):dialog.photo_list.insert('end',f"{i}. {image['original_name']}")
    preview_panel=RoundedPanel(gallery,radius=9,fill='#f7faff',padding=7);preview_panel.pack(fill='both',expand=True)
    dialog.preview=tk.Label(preview_panel.content,text='Chưa có ảnh',bg='#f7faff',fg=NAVY,font=('Segoe UI',-13));dialog.preview.pack(fill='both',expand=True)
    dialog.photo_list.bind('<<ListboxSelect>>',lambda e:dialog.show_photo());dialog.photo_list.bind('<Double-1>',lambda e:dialog.open_original());dialog.preview.bind('<Configure>',lambda e:dialog.show_photo())
    dialog.protocol('WM_DELETE_WINDOW',dialog.close);dialog.bind('<Escape>',lambda e:dialog.close())
    if images:dialog.photo_list.selection_set(0)
    dialog.update_idletasks()
    x=parent.winfo_rootx()+max(0,(parent.winfo_width()-dialog.winfo_width())//2)
    y=parent.winfo_rooty()+max(0,(parent.winfo_height()-dialog.winfo_height())//2)
    dialog.geometry(f'+{x}+{y}');dialog.show_photo();dialog.grab_set();dialog.close_button.focus_force()
