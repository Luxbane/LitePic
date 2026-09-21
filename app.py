import sys,os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk

EXTS = (".jpg",".jpeg",".png",".bmp",".gif",".webp",".tiff",".tif")
MIN_ZOOM = 0.1
MAX_ZOOM = 8.0
BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys,"frozen",False) else Path(__file__).resolve().parent

class LitePic:
    def __init__(self, root, path=None):
        self.root = root
        self.root.title("LitePic")
        icon_path = BASE_DIR / "icon.ico"
        if icon_path.exists():
            try:root.iconbitmap(str(icon_path))
            except Exception:pass

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)
        root.bind("<Control-o>", lambda e: self.open_dialog())

        self.toolbar = tk.Frame(root, bg="#222")
        self.toolbar.pack(side="top", fill="x")
        self.btn_rotate_l = tk.Button(self.toolbar, text="⟲", command=lambda: self.rotate(90))
        self.btn_rotate_r = tk.Button(self.toolbar, text="⟳", command=lambda: self.rotate(-90))
        self.btn_flip_h = tk.Button(self.toolbar, text="⇋", command=lambda: self.mirror("h"))
        self.btn_flip_v = tk.Button(self.toolbar, text="⇵", command=lambda: self.mirror("v"))
        self.btn_crop = tk.Button(self.toolbar, text="✂ Crop", command=self.enter_crop_mode)
        self.btn_undo = tk.Button(self.toolbar, text="↶ Undo", command=self.undo)
        self.btn_redo = tk.Button(self.toolbar, text="↷ Redo", command=self.redo)
        self.btn_saveas = tk.Button(self.toolbar, text="💾 Save As", command=self.save_as)
        for b in (self.btn_rotate_l, self.btn_rotate_r, self.btn_flip_h, self.btn_flip_v, self.btn_crop, self.btn_undo, self.btn_redo, self.btn_saveas):
            b.pack(side="left", padx=2, pady=2)
        self.btn_crop_save = tk.Button(self.toolbar, text="Save crop", command=self.confirm_crop, bg="#2a6")
        self.btn_crop_cancel = tk.Button(self.toolbar, text="Cancel", command=self.cancel_crop, bg="#a33")
        self.root.update_idletasks()
        self.toolbar_h = self.toolbar.winfo_reqheight()

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        self.img = None
        self.tkimg = None
        self.image_id = None
        self.files = []
        self.index = 0
        self.fit_size = (1,1)
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.render_x0 = 0
        self.render_y0 = 0
        self.render_w = 1
        self.render_h = 1

        self.crop_mode = False
        self.crop_start = None
        self.crop_rect_id = None
        self.history = []
        self.future = []

        self.root.bind("<Left>", lambda e: self.nav(-1))
        self.root.bind("<Right>", lambda e: self.nav(1))
        self.root.bind("<Escape>", lambda e: self.cancel_crop() if self.crop_mode else root.destroy())
        self.root.bind("r", lambda e: self.rotate(-90))
        self.root.bind("R", lambda e: self.rotate(-90))
        self.root.bind("l", lambda e: self.rotate(90))
        self.root.bind("L", lambda e: self.rotate(90))
        self.root.bind("h", lambda e: self.mirror("h"))
        self.root.bind("H", lambda e: self.mirror("h"))
        self.root.bind("v", lambda e: self.mirror("v"))
        self.root.bind("V", lambda e: self.mirror("v"))
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_as())

        if path:
            self.open_path(path)

    def scan_folder(self, path):
        folder = os.path.dirname(os.path.abspath(path))
        try:
            names = sorted(f for f in os.listdir(folder) if f.lower().endswith(EXTS))
        except Exception:
            names = [os.path.basename(path)]
        self.files = [os.path.join(folder, n) for n in names]
        try:
            self.index = self.files.index(os.path.abspath(path))
        except ValueError:
            self.files = [os.path.abspath(path)]
            self.index = 0

    def open_path(self, path):
        self.scan_folder(path)
        self.load_current()

    def load_current(self):
        path = self.files[self.index]
        try:
            self.img = Image.open(path)
            self.img.load()
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(200,100,text=f"Can't open:\n{e}",fill="white")
            return
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.history = []
        self.future = []
        self.fit_window_to_image()
        self.render()
        self.root.title(f"LitePic - {os.path.basename(path)}")

    def fit_window_to_image(self):
        w, h = self.img.size
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight() - 60 - self.toolbar_h  # leave room for taskbar + toolbar
        scale = min(1.0, sw / w, sh / h)
        self.fit_size = (max(1,int(w*scale)), max(1,int(h*scale)))
        self.root.geometry(f"{self.fit_size[0]}x{self.fit_size[1] + self.toolbar_h}")

    def render(self):
        w = max(1, int(self.fit_size[0] * self.zoom))
        h = max(1, int(self.fit_size[1] * self.zoom))
        resized = self.img.resize((w,h), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        cw = self.canvas.winfo_width() or w
        ch = self.canvas.winfo_height() or h
        cx = cw//2 + self.offset_x
        cy = ch//2 + self.offset_y
        self.image_id = self.canvas.create_image(cx, cy, anchor="center", image=self.tkimg)
        self.render_w, self.render_h = w, h
        self.render_x0 = cx - w/2
        self.render_y0 = cy - h/2

    def on_resize(self, event):
        if self.image_id is not None:
            cx = event.width//2 + self.offset_x
            cy = event.height//2 + self.offset_y
            self.canvas.coords(self.image_id, cx, cy)
            self.render_x0 = cx - self.render_w/2
            self.render_y0 = cy - self.render_h/2
        elif self.canvas.find_withtag("empty_state"):
            self.canvas.coords("empty_state", event.width//2, event.height//2)

    def on_wheel(self, event):
        if self.img is None or self.crop_mode:return
        factor = 1.1 if event.delta > 0 else (1/1.1)
        new_zoom = min(MAX_ZOOM, max(MIN_ZOOM, self.zoom * factor))
        if new_zoom == self.zoom:return
        self.zoom = new_zoom
        self.offset_x = 0
        self.offset_y = 0
        self.render()

    def on_press(self, event):
        if self.crop_mode:
            self.crop_start = (event.x, event.y)
            if self.crop_rect_id:
                self.canvas.delete(self.crop_rect_id)
            self.crop_rect_id = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline="yellow", dash=(4,2), width=2)
        else:
            self.drag_start = (event.x, event.y)
            self.drag_start_offset = (self.offset_x, self.offset_y)

    def on_drag(self, event):
        if self.crop_mode:
            if self.crop_rect_id and self.crop_start:
                x0,y0 = self.crop_start
                self.canvas.coords(self.crop_rect_id, x0, y0, event.x, event.y)
            return
        if self.image_id is None:return
        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]
        self.offset_x = self.drag_start_offset[0] + dx
        self.offset_y = self.drag_start_offset[1] + dy
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        self.canvas.coords(self.image_id, cw//2 + self.offset_x, ch//2 + self.offset_y)
        self.render_x0 = cw//2 + self.offset_x - self.render_w/2
        self.render_y0 = ch//2 + self.offset_y - self.render_h/2

    def nav(self, step):
        if not self.files or self.crop_mode:return
        self.index = (self.index + step) % len(self.files)
        self.load_current()

    def rotate(self, degrees):
        if self.img is None or self.crop_mode:return
        self.push_history()
        if degrees == -90:
            self.img = self.img.transpose(Image.Transpose.ROTATE_270)
        else:
            self.img = self.img.transpose(Image.Transpose.ROTATE_90)
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_window_to_image()
        self.render()

    def mirror(self, axis):
        if self.img is None or self.crop_mode:return
        self.push_history()
        if axis == "h":
            self.img = self.img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            self.img = self.img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.render()

    def enter_crop_mode(self):
        if self.img is None:return
        self.crop_mode = True
        for b in (self.btn_rotate_l, self.btn_rotate_r, self.btn_flip_h, self.btn_flip_v, self.btn_crop, self.btn_undo, self.btn_redo, self.btn_saveas):
            b.pack_forget()
        self.btn_crop_save.pack(side="left", padx=2, pady=2)
        self.btn_crop_cancel.pack(side="left", padx=2, pady=2)
        self.canvas.config(cursor="crosshair")

    def exit_crop_mode(self):
        self.crop_mode = False
        if self.crop_rect_id:
            self.canvas.delete(self.crop_rect_id)
            self.crop_rect_id = None
        self.crop_start = None
        self.btn_crop_save.pack_forget()
        self.btn_crop_cancel.pack_forget()
        for b in (self.btn_rotate_l, self.btn_rotate_r, self.btn_flip_h, self.btn_flip_v, self.btn_crop, self.btn_undo, self.btn_redo, self.btn_saveas):
            b.pack(side="left", padx=2, pady=2)
        self.canvas.config(cursor="")

    def cancel_crop(self):
        self.exit_crop_mode()

    def confirm_crop(self):
        if not self.crop_rect_id:
            self.exit_crop_mode()
            return
        x0,y0,x1,y1 = self.canvas.coords(self.crop_rect_id)
        sx0,sx1 = sorted((x0,x1))
        sy0,sy1 = sorted((y0,y1))
        scale_disp = self.render_w / self.img.width
        ix0 = (sx0 - self.render_x0) / scale_disp
        iy0 = (sy0 - self.render_y0) / scale_disp
        ix1 = (sx1 - self.render_x0) / scale_disp
        iy1 = (sy1 - self.render_y0) / scale_disp
        ix0 = max(0, min(self.img.width, ix0))
        ix1 = max(0, min(self.img.width, ix1))
        iy0 = max(0, min(self.img.height, iy0))
        iy1 = max(0, min(self.img.height, iy1))
        if ix1 - ix0 < 5 or iy1 - iy0 < 5:
            self.exit_crop_mode()
            return
        self.push_history()
        self.img = self.img.crop((int(ix0), int(iy0), int(ix1), int(iy1)))
        self.exit_crop_mode()
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_window_to_image()
        self.render()

    def push_history(self):
        self.history.append(self.img.copy())
        self.future = []
        if len(self.history) > 20:
            self.history.pop(0)

    def undo(self):
        if self.img is None or self.crop_mode or not self.history:return
        self.future.append(self.img.copy())
        self.img = self.history.pop()
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_window_to_image()
        self.render()

    def redo(self):
        if self.img is None or self.crop_mode or not self.future:return
        self.history.append(self.img.copy())
        self.img = self.future.pop()
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.fit_window_to_image()
        self.render()

    def save_as(self):
        if self.img is None or self.crop_mode:return
        orig = self.files[self.index] if self.files else "image.png"
        base = os.path.splitext(os.path.basename(orig))[0]
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=base + "_edited",
            filetypes=[("PNG","*.png"),("JPEG","*.jpg"),("BMP","*.bmp"),("All files","*.*")])
        if not path:return
        img_to_save = self.img
        if img_to_save.mode == "RGBA" and path.lower().endswith((".jpg",".jpeg")):
            img_to_save = img_to_save.convert("RGB")
        img_to_save.save(path)

    def open_dialog(self):
        path = filedialog.askopenfilename(
            title="Open image",
            filetypes=[("Image files","*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff *.tif"),("All files","*.*")])
        if path:
            self.open_path(path)
            self.show_empty_state(False)

    def show_empty_state(self, show):
        self.canvas.delete("empty_state")
        if show:
            cw = self.canvas.winfo_width() or 600
            ch = self.canvas.winfo_height() or 400
            self.canvas.create_text(cw//2, ch//2, text="No image open\n\nFile > Open (Ctrl+O)",
                fill="white", justify="center", tags="empty_state")

def main():
    root = tk.Tk()
    path = sys.argv[1] if len(sys.argv) > 1 else None
    app = LitePic(root, path)
    if not path:
        root.geometry("500x300")
        root.update_idletasks()
        app.show_empty_state(True)
    root.mainloop()

if __name__ == "__main__":
    main()
