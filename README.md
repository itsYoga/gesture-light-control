# Gesture Light Control / 手勢燈光控制

Control IoTtalk smart bulb brightness using hand gestures detected through your webcam.

透過網路攝影機偵測手勢來控制 IoTtalk 智慧燈泡亮度。

---

## How it works / 運作原理

The program uses MediaPipe to detect your hand and count how many fingers you're holding up. The finger count maps directly to bulb brightness:

程式使用 MediaPipe 偵測手部並計算伸出的手指數量，手指數量直接對應燈泡亮度：

| Fingers / 手指 | Brightness / 亮度 |
|----------------|-------------------|
| 0 (fist / 握拳) | Off / 關閉 |
| 1 | 20% |
| 2 | 40% |
| 3 | 60% |
| 4 | 80% |
| 5 | 100% |

The detected value gets pushed to IoTtalk server, which then controls the connected bulb through a Join function.

偵測到的數值會推送到 IoTtalk 伺服器，透過 Join 函式控制連接的燈泡。

---

## Requirements / 需求

- Python 3.10+
- Webcam / 網路攝影機
- IoTtalk account with a Dummy_Device and Bulb set up / IoTtalk 帳號並設定好 Dummy_Device 和 Bulb

---

## Setup / 安裝

1. Clone this repo and create a virtual environment / 複製此專案並建立虛擬環境：

```bash
git clone https://github.com/itsYoga/gesture-light-control.git
cd gesture-light-control
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies / 安裝相依套件：

```bash
pip install opencv-python mediapipe requests paho-mqtt
```

3. Download the MediaPipe hand model (the script does this automatically on first run):

   下載 MediaPipe 手部模型（程式首次執行時會自動下載）：

```bash
curl -O https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

4. Edit `SA.py` to set your IoTtalk server URL if needed / 如需要可編輯 `SA.py` 設定 IoTtalk 伺服器網址：

```python
ServerURL = 'https://class.iottalk.tw'
```

---

## IoTtalk Setup / IoTtalk 設定

You can use the existing project or create your own:

可以使用現有專案或自行建立：

**Existing project / 現有專案：** Gesture_Light_Control (password / 密碼: 1234) on class.iottalk.tw

Or create your own / 或自行建立：

1. Create a project on IoTtalk with / 在 IoTtalk 建立專案：
   - Input device / 輸入裝置: Dummy_Device (with Dummy_Sensor feature / 含 Dummy_Sensor 功能)
   - Output device / 輸出裝置: Bulb (with Luminance-O feature / 含 Luminance-O 功能)

2. Connect Dummy_Sensor to Luminance-O with a Join / 用 Join 連接 Dummy_Sensor 和 Luminance-O

3. Set the Join function to pass through the value / 設定 Join 函式傳遞數值：

```python
def run(*args):
    return args[0]
```

---

## Usage / 使用方式

```bash
source venv/bin/activate
python gesture_control.py
```

A window will open showing your camera feed with hand tracking overlay. Hold up fingers to control the light. Press 'q' to quit.

視窗會開啟顯示攝影機畫面與手部追蹤。舉起手指控制燈光，按 'q' 鍵退出。

---

## Files / 檔案說明

| File / 檔案 | Description / 說明 |
|-------------|-------------------|
| `gesture_control.py` | Main script with hand detection / 主程式，含手部偵測 |
| `SA.py` | IoTtalk device configuration / IoTtalk 裝置設定 |
| `DAN.py`, `DAI.py`, `csmapi.py` | IoTtalk SDK modules / IoTtalk SDK 模組 |

---

## Notes / 備註

- The camera feed is mirrored so it feels natural (like looking in a mirror)

  攝影機畫面已鏡像，操作起來較自然（像照鏡子）

- There's a small delay/debounce to prevent the brightness from flickering when your hand moves

  有防抖動機制，避免手移動時亮度閃爍

- Make sure your terminal has camera permissions on macOS

  macOS 上請確認終端機有攝影機權限
