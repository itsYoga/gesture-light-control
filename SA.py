"""
手勢控制 IoTtalk 燈泡 - SA 設定檔 (使用 v1 SDK)
Gesture Control for IoTtalk Bulb - SA Configuration
"""

# IoTtalk 伺服器設定
ServerURL = 'https://class.iottalk.tw'

# MQTT 設定 (停用 - 使用純 HTTP)
MQTT_broker = None  # 設為 None 停用 MQTT
MQTT_port = 8883
MQTT_encryption = False
MQTT_User = None
MQTT_PW = None

# 裝置設定
device_model = 'Dummy_Device'
device_name = 'GestureController'
device_id = None  # 使用 MAC 地址

# IDF/ODF 設定
IDF_list = ['Dummy_Sensor']
ODF_list = []

# 推送間隔 (秒)
exec_interval = 1

# 全域變數存放亮度值
luminance_value = 0


def on_register(r):
    print('[IoTtalk] Server: {}'.format(r['server']))
    print('[IoTtalk] Device name: {}'.format(r['d_name']))
    print('[IoTtalk] 裝置註冊成功!')


def Dummy_Sensor():
    """回傳當前亮度值"""
    global luminance_value
    return luminance_value
