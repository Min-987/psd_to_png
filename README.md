# PSD 圖層轉 PNG 工具

將 `.psd` 檔案中的每個圖層，各自匯出為獨立的 `.png` 檔案，並保留圖層在畫布中的原始位置。

## 功能

- 選擇任意 `.psd` 或 `.psb` 檔案
- 自訂輸出資料夾
- 自訂檔名前綴
- 可選擇是否自動編號（`01_`、`02_`…）
- 支援群組圖層，遞迴匯出子圖層
- 每張 PNG 與畫布等大，圖層位置完整保留（含透明度）
- 即時顯示執行記錄

## 使用方式

### 方法一：直接執行 Python 腳本

**安裝依賴：**
```bash
pip install psd-tools
```

**執行程式：**
```bash
python psd_to_png_gui.py
```

### 方法二：打包成 .exe（Windows，不需安裝 Python）

**安裝依賴：**
```bash
pip install pyinstaller psd-tools
```

**打包：**
```bash
pyinstaller --onefile --windowed --name PSD轉PNG psd_to_png_gui.py
```

完成後至 `dist/` 資料夾取得 `PSD轉PNG.exe`，可直接分享給他人使用。

## 系統需求

- Python 3.8 以上
- Windows（GUI 使用 tkinter，內建於 Python）

## 依賴套件

| 套件 | 用途 |
|------|------|
| psd-tools | 解析 PSD 檔案與圖層 |
| Pillow | 影像處理（psd-tools 自動安裝） |
| pyinstaller | 打包成 exe（選用） |
