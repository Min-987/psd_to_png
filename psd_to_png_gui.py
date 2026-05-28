#!/usr/bin/env python3
"""
PSD Layer to PNG Exporter — GUI Version
Build command:
    pip install pyinstaller psd-tools
    pyinstaller --onefile --windowed --name PSD-to-PNG psd_to_png_gui.py
"""

import json
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# ── 顏色 & 字型常數 ──────────────────────────────────────────────
BG        = "#1a1a2e"
PANEL     = "#16213e"
ACCENT    = "#0f3460"
HIGHLIGHT = "#e94560"
TEXT      = "#eaeaea"
MUTED     = "#7a7a9a"
SUCCESS   = "#4ecca3"
WARNING   = "#f5a623"
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_H1   = ("Segoe UI", 14, "bold")
FONT_MONO = ("Consolas", 9)


# ── 設定檔（儲存語言偏好）────────────────────────────────────────
def _config_path() -> Path:
    """設定檔存在 exe 同目錄（或腳本同目錄）"""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / "config.json"

def load_lang() -> str | None:
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
        return data.get("lang")
    except Exception:
        return None

def save_lang(lang: str):
    try:
        _config_path().write_text(json.dumps({"lang": lang}), encoding="utf-8")
    except Exception:
        pass

# ── 語言字串 ────────────────────────────────────────────────────
STRINGS = {
    "zh": {
        "title":          "PSD 圖層轉 PNG",
        "subtitle":       "圖層批次匯出工具",
        "psd_file":       "PSD 檔案",
        "output_folder":  "輸出資料夾",
        "prefix":         "前綴名稱",
        "prefix_hint":    "（可留空）",
        "autonumber":     "自動編號（在檔名前加上 01_ 02_ …）",
        "hint":           "※ 輸出資料夾空白時，自動建立與 PSD 同目錄的「<檔名>_layers」資料夾",
        "browse":         "選擇",
        "start_btn":      "▶  開始匯出",
        "exporting":      "匯出中…",
        "log_title":      "執行記錄",
        "warn_no_psd":    "請先選擇 PSD 檔案！",
        "err_not_found":  "找不到檔案：\n{}",
        "done_msg":       "圖層匯出完畢！\n請查看執行記錄或開啟輸出資料夾。",
        "log_reading":    "📂 讀取檔案：{}",
        "log_canvas":     "   畫布尺寸：{} × {} px",
        "log_output":     "📁 輸出至：{}",
        "log_group":      "{}📁 群組：{}",
        "log_skip":       "{}⚠️  略過（無內容）：{}",
        "log_ok":         "{}✅ {}  (位置 {},{} {}×{})",
        "log_fail":       "{}❌ 失敗：{} — {}",
        "log_done":       "🎉 完成！匯出 {} 個圖層，略過 {} 個",
        "err_no_psdtools":"❌ 找不到 psd-tools，請確認打包步驟是否正確。",
        "err_general":    "❌ 發生錯誤：{}",
        "browse_psd_title":   "選擇 PSD 檔案",
        "browse_psd_types":   [("Photoshop 檔案", "*.psd *.psb"), ("所有檔案", "*.*")],
        "browse_dir_title":   "選擇輸出資料夾",
    },
    "en": {
        "title":          "PSD Layer to PNG",
        "subtitle":       "Batch Layer Exporter",
        "psd_file":       "PSD File",
        "output_folder":  "Output Folder",
        "prefix":         "Prefix",
        "prefix_hint":    "(optional)",
        "autonumber":     "Auto-number filenames (01_, 02_, …)",
        "hint":           "※ If output folder is empty, a \"<filename>_layers\" folder will be created next to the PSD.",
        "browse":         "Browse",
        "start_btn":      "▶  Export Layers",
        "exporting":      "Exporting…",
        "log_title":      "Export Log",
        "warn_no_psd":    "Please select a PSD file first!",
        "err_not_found":  "File not found:\n{}",
        "done_msg":       "Export complete!\nCheck the log or open the output folder.",
        "log_reading":    "📂 Reading: {}",
        "log_canvas":     "   Canvas size: {} × {} px",
        "log_output":     "📁 Output: {}",
        "log_group":      "{}📁 Group: {}",
        "log_skip":       "{}⚠️  Skipped (empty): {}",
        "log_ok":         "{}✅ {}  (pos {},{} {}×{})",
        "log_fail":       "{}❌ Failed: {} — {}",
        "log_done":       "🎉 Done! Exported {} layers, skipped {}",
        "err_no_psdtools":"❌ psd-tools not found. Please check your build setup.",
        "err_general":    "❌ Error: {}",
        "browse_psd_title":   "Select PSD File",
        "browse_psd_types":   [("Photoshop Files", "*.psd *.psb"), ("All Files", "*.*")],
        "browse_dir_title":   "Select Output Folder",
    },
}


# ── 語言選擇視窗 ─────────────────────────────────────────────────
class LangDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.chosen = None
        self.title("")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build()
        self._center(320, 200)

    def _center(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        tk.Frame(self, bg=HIGHLIGHT, height=4).pack(fill="x")

        tk.Label(self, text="PSD → PNG",
                 font=FONT_H1, bg=BG, fg=HIGHLIGHT).pack(pady=(20, 4))
        tk.Label(self, text="Please select a language / 請選擇語言",
                 font=FONT_MAIN, bg=BG, fg=MUTED).pack(pady=(0, 16))

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(padx=32, fill="x")

        tk.Button(
            btn_frame, text="繁體中文",
            font=FONT_BOLD, bg=HIGHLIGHT, fg="white",
            activebackground="#c73652", activeforeground="white",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=lambda: self._pick("zh")
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        tk.Button(
            btn_frame, text="English",
            font=FONT_BOLD, bg=ACCENT, fg="white",
            activebackground="#1a4a80", activeforeground="white",
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=lambda: self._pick("en")
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _pick(self, lang):
        self.chosen = lang
        self.destroy()


# ── 工具函式 ─────────────────────────────────────────────────────
def sanitize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name or "unnamed"


def export_layers(psd_path, output_dir, prefix, autonumber, lang, log_callback, done_callback):
    s = STRINGS[lang]
    try:
        from psd_tools import PSDImage
    except ImportError:
        log_callback(s["err_no_psdtools"], "error")
        done_callback(False)
        return

    try:
        log_callback(s["log_reading"].format(Path(psd_path).name), "info")
        psd = PSDImage.open(psd_path)
        log_callback(s["log_canvas"].format(psd.width, psd.height), "muted")

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        log_callback(s["log_output"].format(out.resolve()), "info")

        exported = [0]
        skipped  = [0]

        def process(layer, depth=0, idx_prefix=""):
            indent = "  " * depth
            safe   = sanitize_name(layer.name)
            fname  = f"{idx_prefix}{safe}.png"
            fpath  = out / fname

            if layer.is_group():
                log_callback(s["log_group"].format(indent, layer.name), "muted")
                for i, child in enumerate(layer):
                    child_pfx = f"{idx_prefix}{safe}_{i+1:02d}_" if autonumber else f"{idx_prefix}{safe}_"
                    process(child, depth + 1, child_pfx)
                return

            try:
                from PIL import Image
                layer_img = layer.composite()
                if layer_img is None:
                    log_callback(s["log_skip"].format(indent, layer.name), "warning")
                    skipped[0] += 1
                    return
                if layer_img.mode != "RGBA":
                    layer_img = layer_img.convert("RGBA")

                canvas = Image.new("RGBA", (psd.width, psd.height), (0, 0, 0, 0))
                x, y = layer.left, layer.top
                canvas.paste(layer_img, (x, y), layer_img)
                canvas.save(str(fpath), "PNG")
                log_callback(s["log_ok"].format(indent, fname, x, y, layer.width, layer.height), "success")
                exported[0] += 1
            except Exception as e:
                log_callback(s["log_fail"].format(indent, layer.name, e), "error")
                skipped[0] += 1

        for i, layer in enumerate(psd):
            if autonumber:
                pfx = f"{prefix}{i+1:02d}_" if prefix else f"{i+1:02d}_"
            else:
                pfx = f"{prefix}_" if prefix else ""
            process(layer, idx_prefix=pfx)

        log_callback("", "info")
        log_callback(s["log_done"].format(exported[0], skipped[0]), "success")
        done_callback(True)

    except Exception as e:
        log_callback(s["err_general"].format(e), "error")
        done_callback(False)


# ── 主視窗 ───────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.s    = STRINGS[lang]
        self.title(self.s["title"])
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center(600, 620)
        self._build_ui()

    def _center(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        s = self.s
        tk.Frame(self, bg=HIGHLIGHT, height=4).pack(fill="x")

        title_frame = tk.Frame(self, bg=BG, pady=16)
        title_frame.pack(fill="x", padx=24)
        tk.Label(title_frame, text="PSD → PNG", font=FONT_H1,
                 bg=BG, fg=HIGHLIGHT).pack(side="left")
        tk.Label(title_frame, text=s["subtitle"], font=FONT_MAIN,
                 bg=BG, fg=MUTED).pack(side="left", padx=10, pady=3)

        form = tk.Frame(self, bg=PANEL, padx=20, pady=16)
        form.pack(fill="x", padx=24, pady=(0, 12))

        self.psd_var        = tk.StringVar()
        self.output_var     = tk.StringVar()
        self.prefix_var     = tk.StringVar()
        self.autonumber_var = tk.BooleanVar(value=True)

        self._row(form, 0, s["psd_file"],      self.psd_var,    self._browse_psd)
        self._row(form, 1, s["output_folder"], self.output_var, self._browse_dir)
        self._prefix_row(form, 2)
        self._checkbox_row(form, 3)

        hint = tk.Frame(self, bg=BG)
        hint.pack(fill="x", padx=24)
        tk.Label(hint, text=s["hint"], font=("Segoe UI", 8),
                 bg=BG, fg=MUTED).pack(anchor="w")

        btn_frame = tk.Frame(self, bg=BG, pady=12)
        btn_frame.pack(fill="x", padx=24)
        self.run_btn = tk.Button(
            btn_frame, text=s["start_btn"],
            font=FONT_BOLD, bg=HIGHLIGHT, fg="white",
            activebackground="#c73652", activeforeground="white",
            relief="flat", bd=0, padx=24, pady=10, cursor="hand2",
            command=self._start
        )
        self.run_btn.pack(fill="x")

        prog_frame = tk.Frame(self, bg=BG)
        prog_frame.pack(fill="x", padx=24, pady=(0, 8))
        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate")
        self.progress.pack(fill="x")
        self._style_progress()

        log_label = tk.Frame(self, bg=BG)
        log_label.pack(fill="x", padx=24)
        tk.Label(log_label, text=s["log_title"], font=FONT_BOLD,
                 bg=BG, fg=MUTED).pack(anchor="w")

        log_frame = tk.Frame(self, bg=PANEL, bd=0)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))

        self.log = tk.Text(
            log_frame, bg=PANEL, fg=TEXT, font=FONT_MONO,
            relief="flat", bd=0, state="disabled",
            wrap="word", padx=10, pady=8,
            insertbackground=TEXT, selectbackground=ACCENT
        )
        scrollbar = tk.Scrollbar(log_frame, command=self.log.yview,
                                  bg=PANEL, troughcolor=PANEL,
                                  activebackground=ACCENT)
        self.log.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        self.log.tag_config("success", foreground=SUCCESS)
        self.log.tag_config("error",   foreground=HIGHLIGHT)
        self.log.tag_config("warning", foreground=WARNING)
        self.log.tag_config("muted",   foreground=MUTED)
        self.log.tag_config("info",    foreground=TEXT)

    def _style_progress(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TProgressbar",
                         troughcolor=PANEL,
                         background=HIGHLIGHT,
                         thickness=4)

    def _row(self, parent, row, label, var, browse_cmd):
        tk.Label(parent, text=label, font=FONT_BOLD,
                 bg=PANEL, fg=TEXT, width=12, anchor="w"
                 ).grid(row=row, column=0, pady=6, sticky="w")
        entry = tk.Entry(parent, textvariable=var, font=FONT_MAIN,
                         bg=ACCENT, fg=TEXT, relief="flat", bd=0,
                         insertbackground=TEXT, selectbackground=HIGHLIGHT)
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 6), ipady=6)
        tk.Button(parent, text=self.s["browse"], font=("Segoe UI", 9),
                  bg=HIGHLIGHT, fg="white", relief="flat", bd=0,
                  padx=10, cursor="hand2", command=browse_cmd
                  ).grid(row=row, column=2)
        parent.columnconfigure(1, weight=1)

    def _prefix_row(self, parent, row):
        s = self.s
        tk.Label(parent, text=s["prefix"], font=FONT_BOLD,
                 bg=PANEL, fg=TEXT, width=12, anchor="w"
                 ).grid(row=row, column=0, pady=6, sticky="w")
        tk.Entry(parent, textvariable=self.prefix_var, font=FONT_MAIN,
                 bg=ACCENT, fg=TEXT, relief="flat", bd=0,
                 insertbackground=TEXT, selectbackground=HIGHLIGHT
                 ).grid(row=row, column=1, sticky="ew", padx=(8, 6), ipady=6)
        tk.Label(parent, text=s["prefix_hint"], font=("Segoe UI", 8),
                 bg=PANEL, fg=MUTED).grid(row=row, column=2, sticky="w")

    def _checkbox_row(self, parent, row):
        tk.Label(parent, text="", bg=PANEL).grid(row=row, column=0)
        tk.Checkbutton(
            parent,
            text=self.s["autonumber"],
            variable=self.autonumber_var,
            font=FONT_MAIN, bg=PANEL, fg=TEXT,
            activebackground=PANEL, activeforeground=TEXT,
            selectcolor=ACCENT, relief="flat", bd=0, cursor="hand2"
        ).grid(row=row, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(2, 4))

    def _browse_psd(self):
        path = filedialog.askopenfilename(
            title=self.s["browse_psd_title"],
            filetypes=self.s["browse_psd_types"]
        )
        if path:
            self.psd_var.set(path)
            if not self.output_var.get():
                p = Path(path)
                self.output_var.set(str(p.parent / f"{p.stem}_layers"))

    def _browse_dir(self):
        path = filedialog.askdirectory(title=self.s["browse_dir_title"])
        if path:
            self.output_var.set(path)

    def _start(self):
        s   = self.s
        psd = self.psd_var.get().strip()
        if not psd:
            messagebox.showwarning(self.s["title"], s["warn_no_psd"])
            return
        if not Path(psd).exists():
            messagebox.showerror(self.s["title"], s["err_not_found"].format(psd))
            return

        output = self.output_var.get().strip()
        if not output:
            p = Path(psd)
            output = str(p.parent / f"{p.stem}_layers")

        prefix = sanitize_name(self.prefix_var.get()) + "_" \
                 if self.prefix_var.get().strip() else ""

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        self.run_btn.configure(state="disabled", text=s["exporting"])
        self.progress.start(12)

        threading.Thread(
            target=export_layers,
            args=(psd, output, prefix, self.autonumber_var.get(),
                  self.lang, self._log, self._done),
            daemon=True
        ).start()

    def _log(self, msg, tag="info"):
        def _append():
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n", tag)
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _append)

    def _done(self, success):
        def _update():
            self.progress.stop()
            self.run_btn.configure(state="normal", text=self.s["start_btn"])
            if success:
                messagebox.showinfo(self.s["title"], self.s["done_msg"])
        self.after(0, _update)


# ── 入口 ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    lang = load_lang()
    if not lang:
        dialog = LangDialog()
        dialog.mainloop()
        lang = dialog.chosen or "en"
        save_lang(lang)
    app = App(lang)
    app.mainloop()