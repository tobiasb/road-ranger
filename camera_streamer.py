"""
Camera streamer for SSH access
Streams camera feed over HTTP so you can view it in a web browser

NOTE: This script requires Picamera2 and must be run with system Python (python3), not pipenv.
Install Picamera2 with: sudo apt install python3-picamera2
Run with: python3 camera_streamer.py
"""

import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import io
import config
import numpy as np
try:
    from picamera2 import Picamera2
except ImportError:
    print("Picamera2 is not installed. Install it with: sudo apt install python3-picamera2")
    exit(1)
import cv2

class CameraStreamer:
    """
    Streams camera feed over HTTP for remote viewing (using Picamera2)
    """

    def __init__(self, port: int = 8080):
        self.port = port
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.server = None
        self.picam = None

    def start(self):
        """Start the camera streamer"""
        print(f"Starting Camera Streamer on port {self.port}...")
        print(f"Open your web browser and go to: http://raspberrypi-ddd.local:{self.port}")
        print("Press Ctrl+C to stop")
        print()

        # Initialize Picamera2
        self.picam = Picamera2()
        config_dict = self.picam.create_preview_configuration(
            main={
                "size": (config.FRAME_WIDTH, config.FRAME_HEIGHT),
                "format": "RGB888"
            },
            buffer_count=2
        )
        self.picam.configure(config_dict)
        self.picam.start()
        time.sleep(2)  # Allow camera to warm-up time
        self.picam.set_controls({"AwbMode": 6})

        # Start camera thread
        self.is_running = True
        camera_thread = threading.Thread(target=self._camera_loop)
        camera_thread.daemon = True
        camera_thread.start()

        # Start HTTP server
        self._start_http_server()

    def stop(self):
        """Stop the camera streamer"""
        self.is_running = False
        if self.picam:
            self.picam.close()
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def _camera_loop(self):
        """Camera capture loop using Picamera2"""
        while self.is_running:
            try:
                frame = self.picam.capture_array()
                with self.frame_lock:
                    self.current_frame = frame.copy()
            except Exception as e:
                print(f"[ERROR] Failed to capture frame: {e}")
                with self.frame_lock:
                    self.current_frame = None
            time.sleep(1.0 / config.FPS)

    def _start_http_server(self):
        """Start HTTP server for streaming"""
        handler = self._create_handler()
        self.server = HTTPServer(('0.0.0.0', self.port), handler)
        print(f"Server started at http://0.0.0.0:{self.port}")
        self.server.serve_forever()

    def _create_handler(self):
        """Create HTTP request handler"""
        streamer = self

        class StreamHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Camera Stream</title>
                        <style>
                            body { margin: 0; padding: 20px; background: #000; }
                            .container { text-align: center; }
                            img { max-width: 100%; height: auto; border: 2px solid #333; }
                            .info { color: white; margin: 10px 0; font-family: Arial, sans-serif; }
                            .controls { margin: 20px 0; }
                            button { margin: 5px; padding: 10px 20px; font-size: 16px; }
                        </style>
                    </head>
                    <body>
                        <div class=\"container\">\n                            <div class=\"info\">\n                                <h2>Camera Stream</h2>\n                                <p>Resolution: """ + f"{config.FRAME_WIDTH}x{config.FRAME_HEIGHT}" + """ | FPS: """ + str(config.FPS) + """</p>\n                            </div>\n                            <img id=\"stream\" src=\"/stream\" alt=\"Camera Stream\">\n                            <div class=\"controls\">\n                                <button onclick=\"location.reload()\">Refresh</button>\n                                <button onclick=\"document.getElementById('stream').src='/stream?' + new Date().getTime()\">Reload Stream</button>\n                            </div>\n                        </div>\n                        <script>\n                            // Auto-refresh the stream every 5 seconds\n                            setInterval(function() {\n                                document.getElementById('stream').src = '/stream?' + new Date().getTime();\n                            }, 5000);\n                        </script>\n                    </body>\n                    </html>\n                    """
                    self.wfile.write(html.encode())

                elif self.path.startswith('/stream'):
                    print("[DEBUG] /stream endpoint hit")
                    with streamer.frame_lock:
                        if streamer.current_frame is not None:
                            print("[DEBUG] Frame available, sending JPEG")
                            # Convert RGB frame to BGR for OpenCV
                            frame_bgr = cv2.cvtColor(streamer.current_frame, cv2.COLOR_RGB2BGR)
                            # Encode as JPEG
                            _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            jpeg_data = buffer.tobytes()

                            self.send_response(200)
                            self.send_header('Content-type', 'image/jpeg')
                            self.send_header('Content-length', str(len(jpeg_data)))
                            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                            self.send_header('Pragma', 'no-cache')
                            self.send_header('Expires', '0')
                            self.end_headers()
                            self.wfile.write(jpeg_data)
                        else:
                            print("[DEBUG] No frame available, returning 404")
                            self.send_response(404)
                            self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress HTTP server logs
                pass

        return StreamHandler


def main():
    """Main entry point"""
    try:
        streamer = CameraStreamer(port=8080)
        streamer.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'streamer' in locals():
            streamer.stop()


if __name__ == "__main__":
    main()