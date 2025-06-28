"""
Timelapse Photo Capture HTTP Endpoint
Simple HTTP endpoint that takes a photo with Picamera2 and stores it with timestamp

NOTE: This script requires Picamera2 and must be run with system Python (python3), not pipenv.
Install Picamera2 with: sudo apt install python3-picamera2
Run with: python3 timelapse_capture.py
"""

import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import config
import cv2
import logging
import os
from datetime import datetime
from typing import Optional, Tuple
import json

try:
    from picamera2 import Picamera2
except ImportError:
    print("Picamera2 is not installed. Install it with: sudo apt install python3-picamera2")
    exit(1)

class TimelapseCapture:
    """
    Simple HTTP endpoint for taking photos with Picamera2 for timelapse creation
    """

    def __init__(self, port: int = 8081,
                 camera_warmup_time: float = 2.0,
                 storage_path: str = "timelapse_photos",
                 photo_width: int = None,
                 photo_height: int = None):
        self.port = port
        self.camera_warmup_time = camera_warmup_time
        self.storage_path = storage_path
        self.photo_width = photo_width
        self.photo_height = photo_height
        self.picam = None

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('timelapse_capture.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _get_max_resolution(self) -> Tuple[int, int]:
        """Get the maximum available resolution for the camera"""
        try:
            # Create temporary Picamera2 instance to get sensor info
            temp_picam = Picamera2()

            # Get camera properties
            sensor_modes = temp_picam.sensor_modes

            # Find the maximum resolution from sensor modes
            max_width = 0
            max_height = 0

            for mode in sensor_modes:
                size = mode.get('size', (0, 0))
                if size[0] * size[1] > max_width * max_height:
                    max_width, max_height = size

            # If no modes found, check camera properties
            if max_width == 0 or max_height == 0:
                camera_props = temp_picam.camera_properties
                pixel_array_size = camera_props.get('PixelArraySize', [1920, 1080])
                max_width = pixel_array_size[0]
                max_height = pixel_array_size[1]

            self.logger.info(f"Camera sensor maximum resolution: {max_width}x{max_height}")

            # Important: Stop and close the temporary instance
            temp_picam.stop()
            temp_picam.close()

            # Add a small delay to ensure camera is fully released
            time.sleep(0.5)

            return max_width, max_height

        except Exception as e:
            self.logger.warning(f"Could not determine max resolution: {e}")
            self.logger.info("Using default high resolution: 4056x3040")
            # Default to Camera Module 3 maximum resolution
            return 4056, 3040

    def start(self):
        """Start the timelapse capture server"""
        # Get maximum resolution if not specified
        if self.photo_width is None or self.photo_height is None:
            self.photo_width, self.photo_height = self._get_max_resolution()

        self.logger.info(f"Starting Timelapse Capture Server on port {self.port}")
        self.logger.info(f"Storage path: {self.storage_path}")
        self.logger.info(f"Camera warmup time: {self.camera_warmup_time}s")
        self.logger.info(f"Photo resolution: {self.photo_width}x{self.photo_height} (MAXIMUM)")
        print(f"Endpoint available at: http://raspberrypi-ddd.local:{self.port}/capture")
        print(f"Using MAXIMUM resolution: {self.photo_width}x{self.photo_height}")
        print("Press Ctrl+C to stop")
        print()

        # Start HTTP server
        self._start_http_server()

    def stop(self):
        """Stop the timelapse capture server"""
        if self.picam:
            self.picam.stop()
            self.picam.close()
        if hasattr(self, 'server') and self.server:
            self.server.shutdown()
            self.server.server_close()

    def _initialize_camera(self):
        """Initialize Picamera2 with maximum resolution settings"""
        try:
            self.picam = Picamera2()

            # Use preview configuration (like camera_streamer.py) for better compatibility
            # but with maximum resolution
            config_dict = self.picam.create_preview_configuration(
                main={
                    "size": (self.photo_width, self.photo_height),
                    "format": "RGB888"
                },
                buffer_count=4
            )
            self.picam.configure(config_dict)
            self.picam.start()

            # Wait for camera to be ready
            self.logger.info(f"Waiting {self.camera_warmup_time}s for camera to warm up...")
            time.sleep(self.camera_warmup_time)

            # Set camera controls
            controls = {"AwbMode": 6}  # Auto white balance

            # Only set these if the camera supports them
            try:
                self.picam.set_controls({"AeEnable": True})  # Auto exposure
                controls["AeEnable"] = True
            except:
                pass

            try:
                self.picam.set_controls({"AfMode": 2})  # Continuous auto focus
                controls["AfMode"] = 2
            except:
                pass

            self.picam.set_controls(controls)

            self.logger.info("Camera initialized successfully with maximum resolution")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False

    def _take_photo(self) -> Optional[str]:
        """Take a single photo and return the file path"""
        if not self.picam:
            if not self._initialize_camera():
                return None

        try:
            # Capture frame at maximum resolution
            frame = self.picam.capture_array()

            # Generate timestamp with milliseconds
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove microseconds, keep milliseconds

            # Create filename
            filename = f"timelapse_{timestamp}.jpg"
            filepath = os.path.join(self.storage_path, filename)

            # Save as JPEG with maximum quality (100)
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])

            self.logger.info(f"Photo captured at {self.photo_width}x{self.photo_height}: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to take photo: {e}")
            return None

    def _start_http_server(self):
        """Start HTTP server for photo capture"""
        handler = self._create_handler()
        self.server = HTTPServer(('0.0.0.0', self.port), handler)
        self.logger.info(f"Server started at http://0.0.0.0:{self.port}")
        self.server.serve_forever()

    def _create_handler(self):
        """Create HTTP request handler"""
        capture = self

        class CaptureHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/capture':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    filepath = capture._take_photo()
                    if filepath:
                        filename = os.path.basename(filepath)
                        response = {
                            'success': True,
                            'filename': filename,
                            'filepath': filepath,
                            'resolution': f"{capture.photo_width}x{capture.photo_height}",
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        response = {
                            'success': False,
                            'error': 'Failed to take photo',
                            'timestamp': datetime.now().isoformat()
                        }

                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress HTTP server logs
                pass

        return CaptureHandler


def main():
    """Main entry point"""
    try:
        # You can customize these settings
        capture = TimelapseCapture(
            port=8081,
            camera_warmup_time=2.0,  # 2 seconds for camera to be ready
            storage_path="timelapse_photos",
            # photo_width and photo_height will be auto-detected to maximum
        )
        capture.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'capture' in locals():
            capture.stop()


if __name__ == "__main__":
    main()