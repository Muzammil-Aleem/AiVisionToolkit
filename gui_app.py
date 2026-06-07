import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from PIL import Image, ImageTk

# ── Tesseract path (adjust if needed) ──────────────────────────────────────
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ───────────────────────────────────────────────────────────────────────────
# THEME
# ───────────────────────────────────────────────────────────────────────────
BG        = "#0f1117"
PANEL     = "#1a1d27"
CARD      = "#22263a"
ACCENT    = "#6c63ff"
ACCENT2   = "#00d4aa"
TEXT      = "#e8eaf6"
SUBTEXT   = "#8892b0"
SUCCESS   = "#00d4aa"
ERROR     = "#ff6b6b"
BORDER    = "#2d3150"
FONT_H    = ("Segoe UI", 22, "bold")
FONT_SUB  = ("Segoe UI", 10)
FONT_BTN  = ("Segoe UI", 11, "bold")
FONT_MONO = ("Consolas", 10)
FONT_LABEL= ("Segoe UI", 9)

# ───────────────────────────────────────────────────────────────────────────
# MAIN APP
# ───────────────────────────────────────────────────────────────────────────
class AIToolkitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Vision Toolkit")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.image_path = tk.StringVar()
        self.confidence = tk.DoubleVar(value=0.5)
        self.mode       = tk.StringVar(value="ocr")

        self._build_ui()

    # ── UI CONSTRUCTION ────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = tk.Frame(self, bg=PANEL, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(sidebar, bg=PANEL, pady=28)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="⬡", font=("Segoe UI", 28), fg=ACCENT,
                 bg=PANEL).pack()
        tk.Label(logo_frame, text="AI Vision Toolkit", font=("Segoe UI", 13, "bold"),
                 fg=TEXT, bg=PANEL).pack()
        tk.Label(logo_frame, text="OCR  ·  Object Detection", font=FONT_LABEL,
                 fg=SUBTEXT, bg=PANEL).pack(pady=(2, 0))

        # Divider
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Mode selector
        mode_frame = tk.Frame(sidebar, bg=PANEL, pady=24, padx=20)
        mode_frame.pack(fill="x")
        tk.Label(mode_frame, text="SELECT MODE", font=("Segoe UI", 8, "bold"),
                 fg=SUBTEXT, bg=PANEL).pack(anchor="w", pady=(0, 10))

        self.ocr_btn = self._mode_btn(mode_frame, "🔤  OCR Extraction", "ocr")
        self.det_btn = self._mode_btn(mode_frame, "🎯  Object Detection", "detect")
        self.ocr_btn.pack(fill="x", pady=(0, 6))
        self.det_btn.pack(fill="x")
        self._highlight_mode()

        # Divider
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # Confidence (only relevant for detection)
        conf_frame = tk.Frame(sidebar, bg=PANEL, padx=20)
        conf_frame.pack(fill="x")
        conf_header = tk.Frame(conf_frame, bg=PANEL)
        conf_header.pack(fill="x")
        tk.Label(conf_header, text="CONFIDENCE THRESHOLD", font=("Segoe UI", 8, "bold"),
                 fg=SUBTEXT, bg=PANEL).pack(side="left")
        self.conf_label = tk.Label(conf_header, text="50%", font=("Segoe UI", 8, "bold"),
                                   fg=ACCENT, bg=PANEL)
        self.conf_label.pack(side="right")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TScale",
                        background=PANEL, troughcolor=CARD,
                        sliderlength=18, sliderrelief="flat")

        self.slider = ttk.Scale(conf_frame, from_=0.1, to=1.0,
                                variable=self.confidence,
                                style="Custom.Horizontal.TScale",
                                command=self._update_conf_label)
        self.slider.pack(fill="x", pady=(6, 0))

        # Divider
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20, pady=16)

        # Image picker
        pick_frame = tk.Frame(sidebar, bg=PANEL, padx=20)
        pick_frame.pack(fill="x")
        tk.Label(pick_frame, text="IMAGE", font=("Segoe UI", 8, "bold"),
                 fg=SUBTEXT, bg=PANEL).pack(anchor="w", pady=(0, 8))

        pick_btn = tk.Button(pick_frame, text="📁  Browse Image",
                             font=FONT_BTN, fg=TEXT, bg=CARD,
                             activebackground=BORDER, activeforeground=TEXT,
                             relief="flat", cursor="hand2", pady=10,
                             command=self._browse)
        pick_btn.pack(fill="x")

        self.path_lbl = tk.Label(pick_frame, text="No file selected",
                                 font=("Segoe UI", 8), fg=SUBTEXT, bg=PANEL,
                                 wraplength=210, justify="left")
        self.path_lbl.pack(anchor="w", pady=(6, 0))

        # Run button (bottom of sidebar)
        sidebar_bottom = tk.Frame(sidebar, bg=PANEL, padx=20, pady=20)
        sidebar_bottom.pack(side="bottom", fill="x")
        self.run_btn = tk.Button(sidebar_bottom, text="▶  Run Analysis",
                                 font=FONT_BTN, fg="white", bg=ACCENT,
                                 activebackground="#5a52d5", activeforeground="white",
                                 relief="flat", cursor="hand2", pady=13,
                                 command=self._run)
        self.run_btn.pack(fill="x")

        # ── Main content area ──────────────────────────────────────────────
        main = tk.Frame(self, bg=BG)
        main.pack(side="right", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main, bg=BG, pady=20, padx=28)
        topbar.pack(fill="x")
        self.title_lbl = tk.Label(topbar, text="OCR Extraction",
                                  font=FONT_H, fg=TEXT, bg=BG)
        self.title_lbl.pack(side="left")

        self.status_dot = tk.Label(topbar, text="●  Ready",
                                   font=("Segoe UI", 9), fg=SUCCESS, bg=BG)
        self.status_dot.pack(side="right", pady=(8, 0))

        # Content panes (image left, output right)
        panes = tk.Frame(main, bg=BG, padx=28)
        panes.pack(fill="both", expand=True, pady=(0, 20))
        panes.columnconfigure(0, weight=1)
        panes.columnconfigure(1, weight=1)
        panes.rowconfigure(0, weight=1)

        # Image preview card
        img_card = tk.Frame(panes, bg=CARD, relief="flat",
                            highlightbackground=BORDER, highlightthickness=1)
        img_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(img_card, text="INPUT IMAGE", font=("Segoe UI", 8, "bold"),
                 fg=SUBTEXT, bg=CARD, pady=12).pack()
        tk.Frame(img_card, bg=BORDER, height=1).pack(fill="x")

        self.img_lbl = tk.Label(img_card, text="No image loaded",
                                font=("Segoe UI", 10), fg=SUBTEXT, bg=CARD)
        self.img_lbl.pack(expand=True)

        # Output card
        out_card = tk.Frame(panes, bg=CARD, relief="flat",
                            highlightbackground=BORDER, highlightthickness=1)
        out_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        out_header = tk.Frame(out_card, bg=CARD)
        out_header.pack(fill="x")
        tk.Label(out_header, text="OUTPUT", font=("Segoe UI", 8, "bold"),
                 fg=SUBTEXT, bg=CARD, pady=12, padx=14).pack(side="left")
        clear_btn = tk.Button(out_header, text="Clear", font=("Segoe UI", 8),
                              fg=SUBTEXT, bg=CARD, activebackground=CARD,
                              activeforeground=TEXT, relief="flat",
                              cursor="hand2", command=self._clear_output)
        clear_btn.pack(side="right", padx=10, pady=8)
        tk.Frame(out_card, bg=BORDER, height=1).pack(fill="x")

        # Notebook: text tab + result image tab
        nb_style = ttk.Style()
        nb_style.configure("Dark.TNotebook", background=CARD, borderwidth=0)
        nb_style.configure("Dark.TNotebook.Tab", background=CARD,
                           foreground=SUBTEXT, padding=[12, 6],
                           font=("Segoe UI", 9))
        nb_style.map("Dark.TNotebook.Tab",
                     background=[("selected", BG)],
                     foreground=[("selected", TEXT)])

        self.nb = ttk.Notebook(out_card, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=2, pady=2)

        # Text tab
        text_tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(text_tab, text="Text Output")
        self.output_box = scrolledtext.ScrolledText(
            text_tab, font=FONT_MONO, bg=BG, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            wrap="word", padx=14, pady=14,
            selectbackground=ACCENT, selectforeground="white"
        )
        self.output_box.pack(fill="both", expand=True)
        self.output_box.configure(state="disabled")

        # Result image tab
        img_tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(img_tab, text="Result Image")
        self.result_lbl = tk.Label(img_tab, text="Run analysis to see result",
                                   font=("Segoe UI", 10), fg=SUBTEXT, bg=BG)
        self.result_lbl.pack(expand=True)

        # Progress bar
        self.progress = ttk.Progressbar(main, mode="indeterminate",
                                        style="TProgressbar")
        pb_style = ttk.Style()
        pb_style.configure("TProgressbar", troughcolor=PANEL,
                           background=ACCENT, thickness=3)
        self.progress.pack(fill="x", side="bottom")

    # ── HELPERS ────────────────────────────────────────────────────────────
    def _mode_btn(self, parent, text, value):
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                        relief="flat", cursor="hand2", pady=11, anchor="w", padx=14,
                        command=lambda v=value: self._set_mode(v))
        return btn

    def _highlight_mode(self):
        m = self.mode.get()
        self.ocr_btn.configure(
            bg=ACCENT if m == "ocr" else CARD,
            fg="white" if m == "ocr" else SUBTEXT)
        self.det_btn.configure(
            bg=ACCENT if m == "detect" else CARD,
            fg="white" if m == "detect" else SUBTEXT)

    def _set_mode(self, value):
        self.mode.set(value)
        self._highlight_mode()
        titles = {"ocr": "OCR Extraction", "detect": "Object Detection"}
        self.title_lbl.configure(text=titles[value])

    def _update_conf_label(self, _=None):
        self.conf_label.configure(text=f"{int(self.confidence.get()*100)}%")

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All files", "*.*")])
        if path:
            self.image_path.set(path)
            self.path_lbl.configure(text=os.path.basename(path), fg=ACCENT2)
            self._show_preview(path)

    def _show_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((380, 320), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.img_lbl.configure(image=photo, text="")
            self.img_lbl._photo = photo
        except Exception as e:
            self.img_lbl.configure(text=f"Preview error: {e}")

    def _clear_output(self):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")
        self.result_lbl.configure(image="", text="Run analysis to see result")
        self.result_lbl._photo = None

    def _set_status(self, text, color=SUCCESS):
        self.status_dot.configure(text=f"●  {text}", fg=color)

    def _log(self, text):
        self.output_box.configure(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.see("end")
        self.output_box.configure(state="disabled")

    # ── RUN ────────────────────────────────────────────────────────────────
    def _run(self):
        if not self.image_path.get():
            messagebox.showwarning("No Image", "Please select an image first.")
            return
        if not os.path.exists(self.image_path.get()):
            messagebox.showerror("File Not Found", "The selected file does not exist.")
            return

        self.run_btn.configure(state="disabled", text="Processing…")
        self.progress.start(12)
        self._set_status("Processing…", ACCENT)
        self._clear_output()

        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()

    def _worker(self):
        try:
            if self.mode.get() == "ocr":
                self._do_ocr()
            else:
                self._do_detect()
        except Exception as e:
            self.after(0, self._on_error, str(e))
        finally:
            self.after(0, self._done)

    def _do_ocr(self):
        import cv2
        import pytesseract

        path = self.image_path.get()
        image = cv2.imread(path)
        if image is None:
            raise FileNotFoundError(f"Cannot open image: {path}")

        self.after(0, self._log, "▸ Preprocessing image…")

        # Preprocessing for white-on-dark images
        gray     = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        scale    = 2
        resized  = cv2.resize(inverted, None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_CUBIC)
        denoised = cv2.fastNlMeansDenoising(resized, h=30)
        thresh   = cv2.threshold(denoised, 0, 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        self.after(0, self._log, "▸ Running Tesseract OCR…")
        text = pytesseract.image_to_string(thresh, config="--psm 6 --oem 3")

        os.makedirs("outputs", exist_ok=True)
        cv2.imwrite("outputs/ocr_processed.png", thresh)
        with open("outputs/extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        result = text.strip() if text.strip() else "⚠ No text detected."
        self.after(0, self._log, "\n── EXTRACTED TEXT ──────────────────\n")
        self.after(0, self._log, result)
        self.after(0, self._log, "\n────────────────────────────────────")
        self.after(0, self._log, "✓ Saved: outputs/extracted_text.txt")
        self.after(0, self._log, "✓ Saved: outputs/ocr_processed.png")
        self.after(0, self._show_result_image, "outputs/ocr_processed.png")
        self.after(0, self._set_status, "OCR Complete", SUCCESS)

    def _do_detect(self):
        from ultralytics import YOLO
        import cv2

        path  = self.image_path.get()
        conf  = self.confidence.get()
        model = YOLO("yolov8n.pt")

        self.after(0, self._log, f"▸ Running YOLOv8 (conf ≥ {conf:.0%})…")

        results = model.predict(source=path, conf=conf)
        image   = cv2.imread(path)
        count   = 0

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf_val = float(box.conf[0])
                cls_id   = int(box.cls[0])
                label    = model.names[cls_id]
                text     = f"{label}: {conf_val:.2f}"

                cv2.rectangle(image, (x1, y1), (x2, y2), (108, 99, 255), 2)
                cv2.rectangle(image, (x1, y1 - 22), (x1 + len(text)*9, y1),
                              (108, 99, 255), -1)
                cv2.putText(image, text, (x1 + 4, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

                self.after(0, self._log, f"  • {label:15s}  {conf_val:.1%}")
                count += 1

        os.makedirs("outputs", exist_ok=True)
        out_path = "outputs/object_detection_output.jpg"
        cv2.imwrite(out_path, image)

        summary = f"\n✓ Detected {count} object(s). Saved: {out_path}"
        self.after(0, self._log, summary)
        self.after(0, self._show_result_image, out_path)
        self.after(0, self._set_status,
                   f"Detection Complete — {count} object(s)", SUCCESS)

    def _show_result_image(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((420, 340), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.result_lbl.configure(image=photo, text="")
            self.result_lbl._photo = photo
            self.nb.select(1)          # switch to Result Image tab
        except Exception:
            pass

    def _on_error(self, msg):
        self._log(f"\n✘ ERROR: {msg}")
        self._set_status("Error", ERROR)
        messagebox.showerror("Error", msg)

    def _done(self):
        self.progress.stop()
        self.run_btn.configure(state="normal", text="▶  Run Analysis")


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = AIToolkitApp()
    app.mainloop()
