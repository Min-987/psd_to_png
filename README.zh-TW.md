繁體中文 | [English](README.md)

---

# PSD 圖層轉 PNG 工具

將 `.psd` 檔案中的每個圖層，各自匯出為獨立的 `.png` 檔案，並保留圖層在畫布中的原始位置。

## 功能

- 選擇任意 `.psd` 或 `.psb` 檔案
- 自訂輸出資料夾
- 自訂檔名前綴
- 可選擇是否自動編號（`01_`、`02_`…）— 預設開啟，可自行勾選關閉
- 支援群組圖層，遞迴匯出子圖層
- 每張 PNG 與畫布等大，圖層位置完整保留（含透明度）
- 即時顯示執行記錄
- 🌐 首次啟動時選擇語言（繁體中文 / English），選擇結果自動儲存

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

## 下載

已編譯的 Windows 執行檔可至 [Releases](../../releases) 頁面下載。

## 語言設定

首次啟動時會跳出語言選擇視窗，選擇後會自動儲存至 exe 同目錄的 `config.json`。若想重新選擇語言，刪除 `config.json` 後重新開啟程式即可。

## 系統需求

- Python 3.8 以上
- Windows（GUI 使用 tkinter，內建於 Python）

## 依賴套件

| 套件 | 用途 |
|------|------|
| psd-tools | 解析 `.psd` 檔案與圖層 |
| Pillow | 影像處理（psd-tools 自動安裝） |
| pyinstaller | 打包成 exe（選用） |

## 更新紀錄

### v1.1.0
- 新增首次啟動語言選擇視窗（繁體中文 / English）
- 語言偏好自動儲存，下次開啟不再詢問

### v1.0.0
- 初始版本
- 將 PSD 圖層各自匯出為 PNG 檔案
- 保留圖層在畫布中的原始位置
- 支援自訂輸出資料夾、檔名前綴、自動編號