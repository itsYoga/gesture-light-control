# Gesture Light Control

Control IoTtalk smart bulb brightness using hand gestures detected through your webcam.

## How it works

The program uses MediaPipe to detect your hand and count how many fingers you're holding up. The finger count maps directly to bulb brightness:

- Fist (0 fingers) - Light off
- 1 finger - 20% brightness
- 2 fingers - 40% brightness
- 3 fingers - 60% brightness
- 4 fingers - 80% brightness
- 5 fingers - 100% brightness

The detected value gets pushed to IoTtalk server, which then controls the connected bulb through a Join function.

## Requirements

- Python 3.10+
- Webcam
- IoTtalk account with a Dummy_Device and Bulb set up

## Setup

1. Clone this repo and create a virtual environment:

```bash
git clone https://github.com/itsYoga/gesture-light-control.git
cd gesture-light-control
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install opencv-python mediapipe requests paho-mqtt
```

3. Download the MediaPipe hand model (the script does this automatically on first run, but you can also grab it manually):

```bash
curl -O https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

4. Edit `SA.py` to set your IoTtalk server URL if needed:

```python
ServerURL = 'https://class.iottalk.tw'
```

## IoTtalk Setup

You can use the existing project or create your own:

**Existing project:** Gesture_Light_Control (password: 1234) on class.iottalk.tw

Or create your own:

1. Create a project on IoTtalk with:
   - Input device: Dummy_Device (with Dummy_Sensor feature)
   - Output device: Bulb (with Luminance-O feature)

2. Connect Dummy_Sensor to Luminance-O with a Join

3. Set the Join function (named "gesture" in the existing project) to pass through the value:

```python
def run(*args):
    return args[0]
```

## Usage

```bash
source venv/bin/activate
python gesture_control.py
```

A window will open showing your camera feed with hand tracking overlay. Hold up fingers to control the light. Press 'q' to quit.

## Files

- `gesture_control.py` - Main script with hand detection and IoTtalk integration
- `SA.py` - IoTtalk device configuration
- `DAN.py`, `DAI.py`, `csmapi.py` - IoTtalk SDK modules

## Notes

- The camera feed is mirrored so it feels natural (like looking in a mirror)
- There's a small delay/debounce to prevent the brightness from flickering when your hand moves
- Make sure your terminal has camera permissions on macOS
