#!/usr/bin/env python3
"""
手勢控制 IoTtalk 燈泡 (使用 v1 SDK)
Gesture Control for IoTtalk Bulb

手勢定義:
- 握拳 (0 指): 關燈 (亮度 = 0)
- 1 指: 亮度 20%
- 2 指: 亮度 40%
- 3 指: 亮度 60%
- 4 指: 亮度 80%
- 5 指 (張開手): 亮度 100%
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import os
import urllib.request
import threading
import sys

# 手指 landmark 索引
FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 6, 10, 14, 18]

# MediaPipe 模型路徑
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# 全域變數
current_luminance = 0
iottalk_connected = False
device_name = "Offline"


def download_model():
    """下載 MediaPipe 手部模型"""
    if not os.path.exists(MODEL_PATH):
        print("正在下載 MediaPipe 手部模型...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("模型下載完成!")
    return MODEL_PATH


class GestureDetector:
    """手勢辨識器"""

    def __init__(self):
        model_path = download_model()

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        self.last_finger_count = 0
        self.stable_count = 0
        self.stability_threshold = 3

    def count_fingers(self, hand_landmarks, handedness):
        """計算伸出的手指數量"""
        fingers = []
        is_right_hand = handedness == "Right"

        # 拇指判斷 - 因為畫面已鏡像翻轉，所以邏輯要反過來
        # 比較拇指尖端與拇指 IP 關節 (index 3) 的 x 座標
        thumb_tip = hand_landmarks[4]
        thumb_ip = hand_landmarks[3]
        index_mcp = hand_landmarks[5]  # 食指根部作為參考

        # 鏡像後：右手在螢幕上看起來像左手
        # 所以實際的右手，拇指向右伸出時 tip.x > ip.x
        if is_right_hand:
            # 鏡像後的右手，拇指伸出時 tip.x > ip.x
            if thumb_tip.x > thumb_ip.x:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            # 鏡像後的左手，拇指伸出時 tip.x < ip.x
            if thumb_tip.x < thumb_ip.x:
                fingers.append(1)
            else:
                fingers.append(0)

        # 其他四指判斷 (y 座標：tip 比 pip 高 = 手指伸出)
        for i in range(1, 5):
            if hand_landmarks[FINGER_TIPS[i]].y < hand_landmarks[FINGER_PIPS[i]].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return sum(fingers)

    def get_stable_count(self, current_count):
        """防抖動取得穩定手指數量"""
        if current_count == self.last_finger_count:
            self.stable_count += 1
        else:
            self.stable_count = 1
            self.last_finger_count = current_count

        if self.stable_count >= self.stability_threshold:
            return current_count
        return -1

    def draw_landmarks(self, frame, hand_landmarks):
        """繪製手部關鍵點"""
        h, w, _ = frame.shape

        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        for start, end in connections:
            x1 = int(hand_landmarks[start].x * w)
            y1 = int(hand_landmarks[start].y * h)
            x2 = int(hand_landmarks[end].x * w)
            y2 = int(hand_landmarks[end].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    def process_frame(self, frame):
        """處理影像幀並偵測手勢"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.detector.detect(mp_image)

        finger_count = -1

        if results.hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.hand_landmarks,
                results.handedness
            ):
                self.draw_landmarks(frame, hand_landmarks)
                hand_type = handedness[0].category_name
                raw_count = self.count_fingers(hand_landmarks, hand_type)
                finger_count = self.get_stable_count(raw_count)

        return frame, finger_count


def finger_count_to_luminance(finger_count):
    """將手指數量轉換為亮度值 (0-255)"""
    return int(finger_count * 51)


def draw_info(frame, finger_count, luminance, connected, dev_name):
    """在畫面上顯示資訊"""
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (350, 180), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    status_color = (0, 255, 0) if connected else (0, 0, 255)
    status_text = f"IoTtalk: {dev_name}" if connected else "IoTtalk: Offline"
    cv2.putText(frame, status_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

    if finger_count >= 0:
        cv2.putText(frame, f"Fingers: {finger_count}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        percent = luminance * 100 // 255
        cv2.putText(frame, f"Luminance: {luminance} ({percent}%)", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        bar_width = int((luminance / 255) * 310)
        cv2.rectangle(frame, (20, 140), (330, 160), (100, 100, 100), -1)
        cv2.rectangle(frame, (20, 140), (20 + bar_width, 160), (0, 255, 255), -1)
    else:
        cv2.putText(frame, "Detecting...", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

    cv2.putText(frame, "Press 'q' to quit", (w - 180, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    return frame


def run_iottalk():
    """在背景執行 IoTtalk 使用 v1 SDK"""
    global iottalk_connected, device_name

    # 添加當前目錄到路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        import DAN
        import SA

        # 設定裝置配置
        DAN.profile['dm_name'] = SA.device_model
        DAN.profile['df_list'] = SA.IDF_list + SA.ODF_list
        if SA.device_name:
            DAN.profile['d_name'] = SA.device_name

        # 設定 MQTT
        if hasattr(SA, 'MQTT_broker') and SA.MQTT_broker:
            DAN.profile['mqtt_enable'] = True

        # 註冊裝置
        result = DAN.device_registration_with_retry(SA.ServerURL, SA.device_id)

        iottalk_connected = True
        device_name = result.get('d_name', 'Connected')

        print("[IoTtalk] 背景服務啟動成功")

        # 使用 HTTP 推送
        while True:
            try:
                luminance = SA.luminance_value
                DAN.push('Dummy_Sensor', [luminance])
                time.sleep(SA.exec_interval)
            except Exception as e:
                print(f"[IoTtalk] 推送錯誤: {e}")
                time.sleep(1)

    except Exception as e:
        print(f"[IoTtalk] 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        iottalk_connected = False


def main():
    global current_luminance, iottalk_connected

    print("=" * 50)
    print("  IoTtalk Gesture-Controlled Bulb")
    print("  手勢控制 IoTtalk 燈泡")
    print("=" * 50)
    print()
    print("手勢說明:")
    print("  握拳 (0 指) -> 關燈")
    print("  1-5 指     -> 20%-100% 亮度")
    print()

    # 切換到腳本目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 啟動 IoTtalk 背景服務
    print("正在連接 IoTtalk 伺服器...")
    iottalk_thread = threading.Thread(target=run_iottalk, daemon=True)
    iottalk_thread.start()
    time.sleep(3)  # 等待連接

    # 初始化手勢辨識器
    print("正在初始化手勢辨識器...")
    detector = GestureDetector()

    # 開啟攝影機
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("錯誤: 無法開啟攝影機")
        print("請確認已授權終端機使用攝影機")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("攝影機已開啟，開始手勢辨識...")
    print("按 'q' 鍵退出")
    print()

    # 導入 SA 模組來更新亮度
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    import SA

    last_luminance = -1

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("錯誤: 無法讀取攝影機畫面")
                break

            frame = cv2.flip(frame, 1)
            frame, finger_count = detector.process_frame(frame)

            luminance = 0
            if finger_count >= 0:
                luminance = finger_count_to_luminance(finger_count)

                if luminance != last_luminance:
                    # 更新 SA 模組中的亮度值
                    SA.luminance_value = luminance
                    current_luminance = luminance
                    print(f"[手勢] 手指: {finger_count}, 亮度: {luminance}")
                    last_luminance = luminance

            frame = draw_info(frame, finger_count, luminance, iottalk_connected, device_name)
            cv2.imshow("Gesture Bulb Controller", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n使用者中斷")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        # 嘗試註銷裝置
        try:
            import DAN
            DAN.deregister()
            print("[IoTtalk] 裝置已註銷")
        except:
            pass
        print("程式結束")


if __name__ == "__main__":
    main()
