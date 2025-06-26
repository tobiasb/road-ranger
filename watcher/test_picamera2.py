import time
try:
    from picamera2 import Picamera2
except ImportError:
    print("Picamera2 is not installed. Install it with: sudo apt install python3-picamera2")
    exit(1)

picam = Picamera2()
picam.start()
time.sleep(2)  # Allow camera to warm up

frame = picam.capture_array()
if frame is not None:
    print("Picamera2 test: Success! Frame captured.")
    print(f"Frame shape: {frame.shape}")
else:
    print("Picamera2 test: Failed to capture frame.")

picam.close()