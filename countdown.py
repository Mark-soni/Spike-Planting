"""
Defuse Countdown Overlay
- Mantén '4' por 2 segundos para activar
- Spike animada centrada encima del contador
- Redimensionable desde la esquina inferior derecha
"""

import sys, ctypes, json, os, time, threading
import tkinter as tk

try:
    import keyboard
except ImportError:
    print("pip install keyboard"); input(); sys.exit(1)
try:
    import cv2
    from PIL import Image, ImageTk
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


TOTAL_SECONDS  = 45
HOLD_SECONDS   = 2
TRIGGER_KEY    = '4'
POLL_INTERVAL  = 0.05

VIDEO_PATH     = r'C:\Users\marce\Downloads\Spike (2).webm'
HALF_CROP      = 380
SPIKE_OFFSET_X = 290

# Tamaño base (escala 1.0)
BASE_W         = 200
BASE_SPIKE     = 150   # tamaño base del video
BASE_FONT      = 44    # tamaño base del numero
BASE_FONT_TITLE= 9

BG       = '#000000'
PANEL_BG = '#111122'
C_RED    = '#e94560'
C_WHITE  = '#ffffff'
C_WARN   = '#ffaa00'
C_CRIT   = '#ff3333'

POS_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'position.json')
SIZE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'size.json')


class CountdownOverlay:
    def __init__(self):
        self.root       = tk.Tk()
        self._timer_id  = None
        self._triggered = False
        self.active     = False
        self.seconds    = TOTAL_SECONDS
        self._running   = True
        self._photo     = None
        self._scale     = 1.0

        self._has_video = CV2_AVAILABLE and bool(VIDEO_PATH)
        if self._has_video:
            self._cap = cv2.VideoCapture(VIDEO_PATH)
            _frames   = self._cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self._fps = _frames / TOTAL_SECONDS

        self._build_window()
        self._build_ui()
        if self._has_video:
            self._start_video()
        self._start_key_monitor()
        self._register_quit_keys()

    # ------------------------------------------------------------------
    # Ventana
    # ------------------------------------------------------------------
    def _build_window(self):
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.93)
        self.root.attributes('-transparentcolor', '#000000')
        self.root.configure(bg=BG)
        self.root.withdraw()

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        # Cargar tamaño guardado
        try:
            sz = json.load(open(SIZE_FILE))
            self._scale = sz.get('scale', 1.0)
        except Exception:
            self._scale = 1.0

        try:
            pos = json.load(open(POS_FILE))
            x, y = pos['x'], pos['y']
        except Exception:
            x = (sw - BASE_W) // 2
            y = sh // 4

        w, h = self._get_win_size()
        self.root.geometry(f'{w}x{h}+{x}+{y}')

        self.root.update_idletasks()
        hwnd = self.root.winfo_id()
        cur  = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, cur | 0x08000000 | 0x00000080)

    def _get_win_size(self):
        w = int(BASE_W * self._scale)
        spike = int(BASE_SPIKE * self._scale)
        panel = int(110 * self._scale)
        h = (spike + panel) if self._has_video else panel
        return w, h

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        if self._has_video:
            spike_frame = tk.Frame(self.root, bg=BG)
            spike_frame.pack(fill='x')
            self.lbl_video = tk.Label(spike_frame, bg='#000000', bd=0)
            self.lbl_video.pack(pady=(6, 0))
            tk.Frame(self.root, bg='#2a2a4a', height=1).pack(fill='x', padx=10)

        panel = tk.Frame(self.root, bg=PANEL_BG, padx=10, pady=6)
        panel.pack(fill='both', expand=True, padx=6, pady=6)

        self.lbl_title = tk.Label(panel, text='DEFUSE',
                                   font=('Segoe UI', BASE_FONT_TITLE, 'bold'),
                                   fg=C_RED, bg=PANEL_BG)
        self.lbl_title.pack()

        self.lbl_time = tk.Label(panel, text=str(TOTAL_SECONDS),
                                  font=('Segoe UI', BASE_FONT, 'bold'),
                                  fg=C_WHITE, bg=PANEL_BG)
        self.lbl_time.pack()

        tk.Label(panel, text='Ctrl+Q ocultar  ·  Ctrl+Shift+Q salir',
                 font=('Segoe UI', 6), fg='#333344', bg=PANEL_BG).pack()

        # Grip de redimensionar (esquina inferior derecha)
        grip = tk.Label(self.root, text='◢', font=('Segoe UI', 10),
                        fg='#334', bg=PANEL_BG, cursor='size_nw_se')
        grip.place(relx=1.0, rely=1.0, anchor='se')
        grip.bind('<ButtonPress-1>',  self._resize_start)
        grip.bind('<B1-Motion>',      self._resize_move)
        grip.bind('<ButtonRelease-1>',self._resize_end)

        # Drag en el panel (excepto grip)
        for w in [panel, self.lbl_title, self.lbl_time]:
            w.bind('<ButtonPress-1>', self._drag_start)
            w.bind('<B1-Motion>',     self._drag_move)

    def _drag_start(self, e):
        self._dx = e.x_root - self.root.winfo_x()
        self._dy = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        x = e.x_root - self._dx
        y = e.y_root - self._dy
        self.root.geometry(f'+{x}+{y}')
        try:
            json.dump({'x': x, 'y': y}, open(POS_FILE, 'w'))
        except Exception:
            pass

    def _resize_start(self, e):
        self._rx = e.x_root
        self._ry = e.y_root
        self._rw = self.root.winfo_width()
        self._rh = self.root.winfo_height()

    def _resize_move(self, e):
        dx   = e.x_root - self._rx
        new_w = max(120, self._rw + dx)
        # Escala basada en el ancho
        self._scale = new_w / BASE_W
        w, h = self._get_win_size()
        self.root.geometry(f'{w}x{h}')
        self._apply_scale()

    def _resize_end(self, e):
        try:
            json.dump({'scale': self._scale}, open(SIZE_FILE, 'w'))
        except Exception:
            pass

    def _apply_scale(self):
        fs       = max(8,  int(BASE_FONT * self._scale))
        fs_title = max(6,  int(BASE_FONT_TITLE * self._scale))
        self.lbl_time.config(font=('Segoe UI', fs, 'bold'))
        self.lbl_title.config(font=('Segoe UI', fs_title, 'bold'))

    # ------------------------------------------------------------------
    # Video
    # ------------------------------------------------------------------
    def _center_spike(self, frame):
        h, w = frame.shape[:2]
        work = frame.copy()
        work[0:90, 0:110] = 0
        work[580:] = 0
        gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 12, 255, cv2.THRESH_BINARY)
        pts = cv2.findNonZero(thresh)
        if pts is not None:
            bx, by, bw, bh = cv2.boundingRect(pts)
            cx = bx + bw // 2
            cy = by + bh // 2
        else:
            cx, cy = w // 2, h // 2
        cx += SPIKE_OFFSET_X
        x1 = max(0, cx - HALF_CROP)
        x2 = min(w,  cx + HALF_CROP)
        y1 = max(0, cy - HALF_CROP)
        y2 = min(h,  cy + HALF_CROP)
        return frame[y1:y2, x1:x2]

    def _start_video(self):
        self._video_tick()

    def _video_tick(self):
        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        if ret:
            sw = int(BASE_SPIKE * self._scale)
            sh = int(BASE_SPIKE * self._scale)
            frame = self._center_spike(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (sw, sh), interpolation=cv2.INTER_LINEAR)
            self._photo = ImageTk.PhotoImage(Image.fromarray(frame))
            self.lbl_video.config(image=self._photo)
        self.root.after(int(1000 / self._fps), self._video_tick)

    # ------------------------------------------------------------------
    # Teclado
    # ------------------------------------------------------------------
    def _start_key_monitor(self):
        threading.Thread(target=self._key_loop, daemon=True).start()

    def _key_loop(self):
        hold_since = None
        while self._running:
            if keyboard.is_pressed(TRIGGER_KEY):
                if hold_since is None:
                    hold_since = time.time()
                elif not self._triggered and time.time() - hold_since >= HOLD_SECONDS:
                    self._triggered = True
                    self.root.after(0, self._trigger)
            else:
                hold_since      = None
                self._triggered = False
            time.sleep(POLL_INTERVAL)

    def _register_quit_keys(self):
        keyboard.add_hotkey('ctrl+q',       lambda: self.root.after(0, self.root.withdraw))
        keyboard.add_hotkey('ctrl+shift+q', lambda: self.root.after(0, self._quit))

    # ------------------------------------------------------------------
    # Contador
    # ------------------------------------------------------------------
    def _trigger(self):
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
        self.active  = True
        self.seconds = TOTAL_SECONDS
        self.lbl_time.config(text=str(TOTAL_SECONDS), fg=C_WHITE)
        self.root.deiconify()
        ctypes.windll.user32.ShowWindow(self.root.winfo_id(), 4)
        self._tick()

    def _tick(self):
        if not self.active:
            return
        color = C_WHITE if self.seconds > 15 else C_WARN if self.seconds > 5 else C_CRIT
        self.lbl_time.config(text=str(self.seconds), fg=color)
        if self.seconds <= 0:
            self.active = False
            self._timer_id = self.root.after(1500, self.root.withdraw)
            return
        self.seconds  -= 1
        self._timer_id = self.root.after(1000, self._tick)

    def _quit(self):
        self._running = False
        if self._has_video:
            self._cap.release()
        keyboard.unhook_all()
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self._running = False
            if self._has_video:
                self._cap.release()
            keyboard.unhook_all()


if __name__ == '__main__':
    CountdownOverlay().run()
