"""
Defuse Countdown Overlay
- Mantén '4' por 2 segundos para activar
- Spike animada centrada encima del contador
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
except ImportError:
    print("pip install opencv-python Pillow"); input(); sys.exit(1)


TOTAL_SECONDS = 45
HOLD_SECONDS  = 2
TRIGGER_KEY   = '4'
POLL_INTERVAL = 0.05

VIDEO_PATH  = r'C:\Users\marce\Downloads\Spike (2).webm'
SPIKE_W     = 150   # tamaño display (cuadrado)
SPIKE_H     = 150
HALF_CROP   = 380   # mitad del recuadro que se recorta alrededor del centro de la spike
SPIKE_OFFSET_X = 290  # negativo = izquierda, positivo = derecha
WIN_W       = 200
WIN_H       = SPIKE_H + 110

BG       = '#000000'  # negro puro = transparente
PANEL_BG = '#111122'  # casi negro pero NO transparente
C_RED    = '#e94560'
C_WHITE  = '#ffffff'
C_WARN   = '#ffaa00'
C_CRIT   = '#ff3333'

POS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'position.json')


class CountdownOverlay:
    def __init__(self):
        self.root       = tk.Tk()
        self._timer_id  = None
        self._triggered = False
        self.active     = False
        self.seconds    = TOTAL_SECONDS
        self._running   = True
        self._photo     = None
        self._cap       = cv2.VideoCapture(VIDEO_PATH)
        _total_frames   = self._cap.get(cv2.CAP_PROP_FRAME_COUNT)
        # FPS ajustado para que el video dure exactamente TOTAL_SECONDS
        self._fps       = _total_frames / TOTAL_SECONDS

        self._build_window()
        self._build_ui()
        self._start_video()
        self._start_key_monitor()
        self._register_quit_keys()

    # ------------------------------------------------------------------
    def _build_window(self):
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.93)
        self.root.attributes('-transparentcolor', '#000000')
        self.root.configure(bg=BG)
        self.root.withdraw()

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        try:
            pos = json.load(open(POS_FILE))
            x, y = pos['x'], pos['y']
        except Exception:
            x = (sw - WIN_W) // 2
            y = sh // 4

        self.root.geometry(f'{WIN_W}x{WIN_H}+{x}+{y}')
        self.root.bind('<ButtonPress-1>', lambda e: setattr(self, '_dx', e.x) or setattr(self, '_dy', e.y))
        self.root.bind('<B1-Motion>',     self._drag)

        self.root.update_idletasks()
        hwnd = self.root.winfo_id()
        cur  = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, cur | 0x08000000 | 0x00000080)

    def _drag(self, e):
        x = self.root.winfo_x() + e.x - self._dx
        y = self.root.winfo_y() + e.y - self._dy
        self.root.geometry(f'+{x}+{y}')
        try:
            json.dump({'x': x, 'y': y}, open(POS_FILE, 'w'))
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Spike centrada arriba
        spike_frame = tk.Frame(self.root, bg=BG)
        spike_frame.pack(fill='x')

        self.lbl_video = tk.Label(spike_frame, bg='#000000', bd=0)
        self.lbl_video.pack(pady=(6, 0))

        # Separador
        tk.Frame(self.root, bg='#2a2a4a', height=1).pack(fill='x', padx=10)

        # Panel contador
        panel = tk.Frame(self.root, bg=PANEL_BG, padx=10, pady=6)
        panel.pack(fill='both', expand=True, padx=6, pady=6)

        tk.Label(panel, text='DEFUSE', font=('Segoe UI', 9, 'bold'),
                 fg=C_RED, bg=PANEL_BG).pack()

        self.lbl_time = tk.Label(panel, text=str(TOTAL_SECONDS),
                                  font=('Segoe UI', 44, 'bold'),
                                  fg=C_WHITE, bg=PANEL_BG)
        self.lbl_time.pack()

        tk.Label(panel, text='Ctrl+Q ocultar  ·  Ctrl+Shift+Q salir',
                 font=('Segoe UI', 6), fg='#333344', bg=PANEL_BG).pack()

    # ------------------------------------------------------------------
    def _center_spike(self, frame):
        """Detecta donde esta la Spike en el frame y recorta centrado en ella."""
        h, w = frame.shape[:2]
        work = frame.copy()
        work[0:90, 0:110] = 0   # borrar gizmo Y/Z/X
        work[580:] = 0           # borrar patitas
        gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 12, 255, cv2.THRESH_BINARY)
        pts = cv2.findNonZero(thresh)
        if pts is not None:
            bx, by, bw, bh = cv2.boundingRect(pts)
            cx = bx + bw // 2
            cy = by + bh // 2
        else:
            cx, cy = w // 2, h // 2
        # Recortar un cuadrado de HALF_CROP*2 centrado en la Spike
        cx += SPIKE_OFFSET_X
        x1 = max(0, cx - HALF_CROP)
        x2 = min(w,  cx + HALF_CROP)
        y1 = max(0, cy - HALF_CROP)
        y2 = min(h,  cy + HALF_CROP)
        return frame[y1:y2, x1:x2]

    # ------------------------------------------------------------------
    def _start_video(self):
        self._video_tick()

    def _video_tick(self):
        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        if ret:
            frame = self._center_spike(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (SPIKE_W, SPIKE_H), interpolation=cv2.INTER_LINEAR)
            self._photo = ImageTk.PhotoImage(Image.fromarray(frame))
            self.lbl_video.config(image=self._photo)
        self.root.after(int(1000 / self._fps), self._video_tick)

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
        self._cap.release()
        keyboard.unhook_all()
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self._running = False
            self._cap.release()
            keyboard.unhook_all()


if __name__ == '__main__':
    CountdownOverlay().run()
