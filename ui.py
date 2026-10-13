"""Small native Tk components with rounded, antialiased surfaces."""
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

BLUE = '#1677ee'
NAVY = '#193d67'
MUTED = '#74889f'
PAGE = '#edf4fb'
LINE = '#d6e3f0'
FONT = ('Segoe UI', -15)


def rounded_image(width, height, radius, fill, border=None, dashed=False):
    scale = 3
    image = Image.new('RGBA', (max(1, width)*scale, max(1, height)*scale))
    draw = ImageDraw.Draw(image)
    box = (1, 1, width*scale-2, height*scale-2)
    draw.rounded_rectangle(box, radius=radius*scale, fill=fill, outline=border, width=scale)
    if dashed:
        # A separate dashed outline follows all four straight sides.
        for x in range(radius+3, width-radius, 10):
            for y in (1, height-2):
                draw.line((x*scale,y*scale,min(x+5,width-radius)*scale,y*scale),fill=BLUE,width=scale)
        for y in range(radius+3,height-radius,10):
            for x in (1,width-2):
                draw.line((x*scale,y*scale,x*scale,min(y+5,height-radius)*scale),fill=BLUE,width=scale)
    return ImageTk.PhotoImage(image.resize((max(1,width),max(1,height)),Image.Resampling.LANCZOS))


def icon(master, kind, size=20, color=BLUE):
    s=4
    im=Image.new('RGBA',(size*s,size*s))
    d=ImageDraw.Draw(im)
    def line(points,width=1.6): d.line([(int(x*size*s/24),int(y*size*s/24)) for x,y in points],fill=color,width=max(1,int(width*size*s/24)),joint='curve')
    def ellipse(box, fill=None): d.ellipse(tuple(int(v*size*s/24) for v in box),fill=fill,outline=color,width=max(1,int(1.5*size*s/24)))
    def rect(box): d.rounded_rectangle(tuple(int(v*size*s/24) for v in box),radius=2*s,outline=color,width=max(1,int(1.5*size*s/24)))
    if kind=='people':
        ellipse((8,3,16,11),color); ellipse((1,6,7,12),color); ellipse((17,6,23,12),color)
        d.rounded_rectangle((6*size*s//24,12*size*s//24,18*size*s//24,22*size*s//24),radius=4*s,fill=color)
        line([(1,21),(1,17),(4,14),(6,14)],3); line([(23,21),(23,17),(20,14),(18,14)],3)
    elif kind=='search': ellipse((3,3,16,16)); line([(15,15),(22,22)],2)
    elif kind=='eye':
        line([(2,12),(6,7),(12,5),(18,7),(22,12),(18,17),(12,19),(6,17),(2,12)]); ellipse((9,9,15,15))
    elif kind=='edit': line([(5,16),(16,5),(20,9),(9,20),(4,21),(5,16),(9,20)]); line([(14,7),(18,11)])
    elif kind=='delete': line([(4,6),(20,6)]); line([(8,6),(8,3),(16,3),(16,6)]); line([(6,7),(7,21),(17,21),(18,7)]); line([(10,10),(10,18)]); line([(14,10),(14,18)])
    elif kind=='save': rect((3,3,21,21)); rect((7,3,16,9)); rect((7,14,17,21))
    elif kind=='image': rect((2,3,22,21)); ellipse((14,6,18,10)); line([(3,18),(9,11),(14,16),(17,13),(22,18)])
    elif kind=='plus': ellipse((2,2,22,22),color); color='white'; line([(12,7),(12,17)],2); line([(7,12),(17,12)],2)
    elif kind=='user': ellipse((8,3,16,11)); line([(3,22),(3,18),(7,14),(17,14),(21,18),(21,22)])
    elif kind=='phone': line([(7,3),(3,6),(5,13),(11,19),(18,22),(22,18),(17,14),(14,17),(8,11),(10,8),(7,3)])
    elif kind=='id': rect((2,5,22,20)); ellipse((5,8,10,13)); line([(4,17),(11,17)]); line([(14,10),(19,10)]); line([(14,15),(19,15)])
    elif kind=='open': rect((3,8,17,21)); line([(11,3),(22,3),(22,14)]); line([(22,3),(10,15)])
    return ImageTk.PhotoImage(im.resize((size,size),Image.Resampling.LANCZOS),master=master)


class RoundedPanel(tk.Canvas):
    def __init__(self, master, radius=14, fill='white', border=LINE, padding=1, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, bg=master.cget('bg'), **kwargs)
        self.radius,self.fill,self.border,self.padding=radius,fill,border,padding
        self.content=tk.Frame(self,bg=fill)
        self.bind('<Configure>',self.draw)
    def draw(self,event=None):
        w,h=self.winfo_width(),self.winfo_height()
        self.surface=rounded_image(w,h,self.radius,self.fill,self.border)
        self.delete('surface'); self.create_image(0,0,image=self.surface,anchor='nw',tags='surface'); self.tag_lower('surface')
        self.content.place(x=self.padding,y=self.radius,width=max(1,w-2*self.padding),height=max(1,h-2*self.radius))


class RoundButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=110, height=36, primary=False, danger=False, icon_name=None, style='', **kwargs):
        super().__init__(master,width=width,height=max(32,height),bg=master.cget('bg'),highlightthickness=0,bd=0,takefocus=1,cursor='hand2',**kwargs)
        self.text,self.command,self.primary,self.danger,self.style=text,command,primary,danger,style
        self.disabled=False; self.hover=False
        self.icon_name=icon_name
        self.bind('<Configure>',self.draw)
        self.bind('<Enter>',lambda e:self.set_hover(True)); self.bind('<Leave>',lambda e:self.set_hover(False))
        self.bind('<ButtonRelease-1>',lambda e:self.invoke())
        self.bind('<space>',lambda e:self.invoke()); self.bind('<Return>',lambda e:self.invoke())
        self.bind('<FocusIn>',self.draw); self.bind('<FocusOut>',self.draw)
    def set_hover(self,value): self.hover=value; self.draw()
    def draw(self,event=None):
        self.delete('all')
        fg='#97a8bc' if self.disabled else ('white' if self.primary else ('#cb4659' if self.danger else '#2468b0'))
        fill=('#edf2f7' if self.disabled else ('#0964d5' if self.hover else BLUE)) if self.primary else ('#fff0f2' if self.danger else ('#dfedfc' if self.hover else '#f0f6fd'))
        self.surface=rounded_image(self.winfo_width(),self.winfo_height(),7,fill,BLUE if self.focus_get()==self else ('#f0d7df' if self.danger else LINE))
        self.create_image(0,0,image=self.surface,anchor='nw')
        import tkinter.font as tf
        font=('Segoe UI',-14,'bold' if self.primary else 'normal')
        length=tf.Font(font=font).measure(self.text)+(24 if self.icon_name else 0)
        start=(self.winfo_width()-length)/2
        if self.icon_name:
            self.glyph=icon(self,self.icon_name,19,fg); self.create_image(start+9,self.winfo_height()/2,image=self.glyph); start+=24
        self.create_text(start,self.winfo_height()/2,text=self.text,fill=fg,font=font,anchor='w')
    def invoke(self):
        if not self.disabled and self.command: return self.command()
    def cget(self,key):
        if key=='text': return self.text
        if key=='style': return self.style
        return super().cget(key)
    def configure(self,cnf=None,**kwargs):
        if 'text' in kwargs: self.text=kwargs.pop('text')
        super().configure(cnf,**kwargs); self.draw()
    config=configure
    def state(self,values): self.disabled='disabled' in values; self.draw()
    def instate(self,values): return self.disabled if 'disabled' in values else not self.disabled


def label(master,text='',bold=False,size=15,muted=False,**kwargs):
    return tk.Label(master,text=text,bg=master.cget('bg'),fg=MUTED if muted else NAVY,font=('Segoe UI',-size,'bold' if bold else 'normal'),**kwargs)


class RoundEntry(RoundedPanel):
    def __init__(self,master,variable,placeholder='',icon_name=None,readonly=False,height=35):
        super().__init__(master,radius=7,fill='#f7faff' if readonly else 'white',height=height)
        self.content.destroy()
        self.entry=tk.Entry(self,textvariable=variable,relief='flat',bd=0,font=FONT,fg=NAVY,bg=self.fill,readonlybackground=self.fill)
        if readonly:self.entry.configure(state='readonly')
        self.entry.place(x=34 if icon_name else 10,y=7,relwidth=1,width=-44 if icon_name else -20,height=height-14)
        self.icon_name=icon_name
        self.hint=tk.Label(self,text=placeholder,font=FONT,fg=MUTED,bg=self.fill,anchor='w')
        self.hint.bind('<Button-1>',lambda e:self.entry.focus_set())
        def update(*args):
            if variable.get() or self.entry.focus_get()==self.entry:self.hint.place_forget()
            else:self.hint.place(x=34 if icon_name else 10,y=7,relwidth=1,width=-44 if icon_name else -20,height=height-14)
        variable.trace_add('write',update)
        self.entry.bind('<FocusIn>',update);self.entry.bind('<FocusOut>',update)
        self.bind('<Configure>',lambda e:(self.draw(),update()))
    def draw(self,event=None):
        self.surface=rounded_image(self.winfo_width(),self.winfo_height(),7,self.fill,LINE)
        self.delete('all');self.create_image(0,0,image=self.surface,anchor='nw')
        if self.icon_name:
            self.glyph=icon(self,self.icon_name,20,'#87a0bd');self.create_image(17,self.winfo_height()/2,image=self.glyph)


class ImageChooser(tk.Canvas):
    def __init__(self,master,command):
        super().__init__(master,bg=master.cget('bg'),highlightthickness=0,height=106,cursor='hand2',takefocus=1)
        self.command=command
        self.bind('<Configure>',self.draw);self.bind('<ButtonRelease-1>',lambda e:command());self.bind('<Return>',lambda e:command())
    def draw(self,event=None):
        w,h=self.winfo_width(),self.winfo_height();self.delete('all')
        self.surface=rounded_image(w,h,9,'#f6faff',dashed=True)
        self.create_image(0,0,image=self.surface,anchor='nw')
        self.glyph=icon(self,'image',30);self.create_image(w/2,24,image=self.glyph)
        self.create_text(w/2,51,text='Chọn ảnh',font=('Segoe UI',-16,'bold'),fill=BLUE)
        self.create_text(w/2,74,text='Nhấp để chọn một hoặc nhiều ảnh',font=('Segoe UI',-13),fill=MUTED)
        self.create_text(w/2,94,text='JPG, PNG, WEBP, BMP',font=('Segoe UI',-12),fill=MUTED)
