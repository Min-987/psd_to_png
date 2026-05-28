#!/usr/bin/env python3
"""
PSD 圖層轉 PNG — GUI 版本
打包指令（在程式同目錄執行）：
    pip install pyinstaller psd-tools
    pyinstaller --onefile --windowed --name PSD轉PNG psd_to_png_gui.py
"""

import re
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


# ── 工具函式 ─────────────────────────────────────────────────────
def sanitize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    return name or "unnamed"


def export_layers(psd_path, output_dir, prefix, autonumber, log_callback, done_callback):
    """在子執行緒中執行圖層匯出"""
    try:
        from psd_tools import PSDImage
    except ImportError:
        log_callback("❌ 找不到 psd-tools，請確認打包步驟是否正確。", "error")
        done_callback(False)
        return

    try:
        log_callback(f"📂 讀取檔案：{Path(psd_path).name}", "info")
        psd = PSDImage.open(psd_path)
        log_callback(f"   畫布尺寸：{psd.width} × {psd.height} px", "muted")

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        log_callback(f"📁 輸出至：{out.resolve()}", "info")

        exported = [0]
        skipped  = [0]

        def process(layer, depth=0, idx_prefix=""):
            indent = "  " * depth
            safe   = sanitize_name(layer.name)
            fname  = f"{idx_prefix}{safe}.png"
            fpath  = out / fname

            if layer.is_group():
                log_callback(f"{indent}📁 群組：{layer.name}", "muted")
                for i, child in enumerate(layer):
                    child_pfx = f"{idx_prefix}{safe}_{i+1:02d}_" if autonumber else f"{idx_prefix}{safe}_"
                    process(child, depth + 1, child_pfx)
                return

            try:
                from PIL import Image
                layer_img = layer.composite()
                if layer_img is None:
                    log_callback(f"{indent}⚠️  略過（無內容）：{layer.name}", "warning")
                    skipped[0] += 1
                    return
                if layer_img.mode != "RGBA":
                    layer_img = layer_img.convert("RGBA")

                # 建立與畫布同尺寸的透明底圖，再將圖層貼到正確位置
                canvas = Image.new("RGBA", (psd.width, psd.height), (0, 0, 0, 0))
                x, y = layer.left, layer.top
                canvas.paste(layer_img, (x, y), layer_img)
                canvas.save(str(fpath), "PNG")
                log_callback(f"{indent}✅ {fname}  (位置 {x},{y}  {layer.width}×{layer.height})", "success")
                exported[0] += 1
            except Exception as e:
                log_callback(f"{indent}❌ 失敗：{layer.name} — {e}", "error")
                skipped[0] += 1

        for i, layer in enumerate(psd):
            if autonumber:
                pfx = f"{prefix}{i+1:02d}_" if prefix else f"{i+1:02d}_"
            else:
                pfx = f"{prefix}_" if prefix else ""
            process(layer, idx_prefix=pfx)

        log_callback("", "info")
        log_callback(
            f"🎉 完成！匯出 {exported[0]} 個圖層，略過 {skipped[0]} 個",
            "success"
        )
        done_callback(True)

    except Exception as e:
        log_callback(f"❌ 發生錯誤：{e}", "error")
        done_callback(False)


# ── 主視窗 ───────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PSD 圖層轉 PNG")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center(600, 620)
        self._build_ui()

    def _center(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── UI 建構 ──────────────────────────────────────────────────
    def _build_ui(self):
        # 標題列
        header = tk.Frame(self, bg=HIGHLIGHT, height=4)
        header.pack(fill="x")

        title_frame = tk.Frame(self, bg=BG, pady=16)
        title_frame.pack(fill="x", padx=24)
        tk.Label(title_frame, text="PSD → PNG", font=FONT_H1,
                 bg=BG, fg=HIGHLIGHT).pack(side="left")
        tk.Label(title_frame, text="圖層批次匯出工具", font=FONT_MAIN,
                 bg=BG, fg=MUTED).pack(side="left", padx=10, pady=3)

        # 表單區
        form = tk.Frame(self, bg=PANEL, padx=20, pady=16)
        form.pack(fill="x", padx=24, pady=(0, 12))

        self.psd_var        = tk.StringVar()
        self.output_var     = tk.StringVar()
        self.prefix_var     = tk.StringVar()
        self.autonumber_var = tk.BooleanVar(value=True)

        self._row(form, 0, "PSD 檔案",   self.psd_var,    self._browse_psd)
        self._row(form, 1, "輸出資料夾", self.output_var, self._browse_dir)
        self._prefix_row(form, 2)
        self._checkbox_row(form, 3)

        # 說明文字
        hint = tk.Frame(self, bg=BG)
        hint.pack(fill="x", padx=24)
        tk.Label(hint,
                 text="※ 輸出資料夾空白時，自動建立與 PSD 同目錄的「<檔名>_layers」資料夾",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(anchor="w")

        # 執行按鈕
        btn_frame = tk.Frame(self, bg=BG, pady=12)
        btn_frame.pack(fill="x", padx=24)
        self.run_btn = tk.Button(
            btn_frame, text="▶  開始匯出",
            font=FONT_BOLD, bg=HIGHLIGHT, fg="white",
            activebackground="#c73652", activeforeground="white",
            relief="flat", bd=0, padx=24, pady=10, cursor="hand2",
            command=self._start
        )
        self.run_btn.pack(fill="x")

        # 進度條
        prog_frame = tk.Frame(self, bg=BG)
        prog_frame.pack(fill="x", padx=24, pady=(0, 8))
        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate")
        self.progress.pack(fill="x")
        self._style_progress()

        # 日誌區
        log_label = tk.Frame(self, bg=BG)
        log_label.pack(fill="x", padx=24)
        tk.Label(log_label, text="執行記錄", font=FONT_BOLD,
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

        # 設定 tag 顏色
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
                 bg=PANEL, fg=TEXT, width=10, anchor="w"
                 ).grid(row=row, column=0, pady=6, sticky="w")

        entry = tk.Entry(parent, textvariable=var, font=FONT_MAIN,
                         bg=ACCENT, fg=TEXT, relief="flat", bd=0,
                         insertbackground=TEXT, selectbackground=HIGHLIGHT)
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 6), ipady=6)

        btn = tk.Button(parent, text="選擇", font=("Segoe UI", 9),
                        bg=HIGHLIGHT, fg="white", relief="flat", bd=0,
                        padx=10, cursor="hand2", command=browse_cmd)
        btn.grid(row=row, column=2)
        parent.columnconfigure(1, weight=1)

    def _prefix_row(self, parent, row):
        tk.Label(parent, text="前綴名稱", font=FONT_BOLD,
                 bg=PANEL, fg=TEXT, width=10, anchor="w"
                 ).grid(row=row, column=0, pady=6, sticky="w")

        entry = tk.Entry(parent, textvariable=self.prefix_var, font=FONT_MAIN,
                         bg=ACCENT, fg=TEXT, relief="flat", bd=0,
                         insertbackground=TEXT, selectbackground=HIGHLIGHT)
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 6), ipady=6)

        tk.Label(parent, text="（可留空）", font=("Segoe UI", 8),
                 bg=PANEL, fg=MUTED).grid(row=row, column=2, sticky="w")

    def _checkbox_row(self, parent, row):
        tk.Label(parent, text="", bg=PANEL
                 ).grid(row=row, column=0)
        cb = tk.Checkbutton(
            parent,
            text="自動編號（在檔名前加上 01_ 02_ …）",
            variable=self.autonumber_var,
            font=FONT_MAIN,
            bg=PANEL, fg=TEXT,
            activebackground=PANEL, activeforeground=TEXT,
            selectcolor=ACCENT,
            relief="flat", bd=0, cursor="hand2"
        )
        cb.grid(row=row, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(2, 4))

    # ── 動作 ─────────────────────────────────────────────────────
    def _browse_psd(self):
        path = filedialog.askopenfilename(
            title="選擇 PSD 檔案",
            filetypes=[("Photoshop 檔案", "*.psd *.psb"), ("所有檔案", "*.*")]
        )
        if path:
            self.psd_var.set(path)
            # 自動填入輸出路徑
            if not self.output_var.get():
                p = Path(path)
                self.output_var.set(str(p.parent / f"{p.stem}_layers"))

    def _browse_dir(self):
        path = filedialog.askdirectory(title="選擇輸出資料夾")
        if path:
            self.output_var.set(path)

    def _start(self):
        psd = self.psd_var.get().strip()
        if not psd:
            messagebox.showwarning("提示", "請先選擇 PSD 檔案！")
            return
        if not Path(psd).exists():
            messagebox.showerror("錯誤", f"找不到檔案：\n{psd}")
            return

        output = self.output_var.get().strip()
        if not output:
            p = Path(psd)
            output = str(p.parent / f"{p.stem}_layers")

        prefix = sanitize_name(self.prefix_var.get()) + "_" \
                 if self.prefix_var.get().strip() else ""

        # 清空日誌
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        self.run_btn.configure(state="disabled", text="匯出中…")
        self.progress.start(12)

        threading.Thread(
            target=export_layers,
            args=(psd, output, prefix, self.autonumber_var.get(), self._log, self._done),
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
            self.run_btn.configure(state="normal", text="▶  開始匯出")
            if success:
                messagebox.showinfo("完成", "圖層匯出完畢！\n請查看執行記錄或開啟輸出資料夾。")
        self.after(0, _update)


# ── 入口 ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()