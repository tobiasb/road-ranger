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
import cv2
import logging
from typing import Optional, Callable, Tuple

try:
    from picamera2 import Picamera2
except ImportError:
    print("Picamera2 is not installed. Install it with: sudo apt install python3-picamera2")
    exit(1)

class CameraStreamer:
    """
    Streams camera feed over HTTP for remote viewing (using Picamera2)
    Optimized for lens calibration with higher resolution and faster refresh
    """

    def __init__(self, port: int = 8080):
        self.port = port
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.server = None
        self.picam = None

        # Calibration-optimized settings
        self.calibration_width = 1920  # Higher resolution for calibration
        self.calibration_height = 1080
        self.calibration_fps = 30  # Higher FPS for responsiveness
        self.stream_quality = 90  # Higher JPEG quality for calibration

    def start(self):
        """Start the camera streamer"""
        print(f"Starting Camera Streamer on port {self.port}...")
        print(f"Open your web browser and go to: http://raspberrypi-ddd.local:{self.port}")
        print(f"Calibration Mode: {self.calibration_width}x{self.calibration_height} @ {self.calibration_fps}fps")
        print("Press Ctrl+C to stop")
        print()

        # Initialize Picamera2 with calibration settings
        self.picam = Picamera2()
        config_dict = self.picam.create_preview_configuration(
            main={
                "size": (self.calibration_width, self.calibration_height),
                "format": "RGB888"
            },
            buffer_count=4  # More buffers for smoother streaming
        )
        self.picam.configure(config_dict)
        self.picam.start()
        time.sleep(1)  # Reduced warm-up time
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
        """Camera capture loop using Picamera2 - optimized for calibration"""
        while self.is_running:
            try:
                if self.picam is not None:
                    frame = self.picam.capture_array()
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                else:
                    print("[WARNING] Camera not initialized")
                    time.sleep(0.1)
            except Exception as e:
                print(f"[ERROR] Failed to capture frame: {e}")
                with self.frame_lock:
                    self.current_frame = None
            time.sleep(1.0 / self.calibration_fps)  # Use calibration FPS

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
                        <title>Camera Stream - Calibration Mode</title>
                        <style>
                            body { margin: 0; padding: 20px; background: #000; }
                            .container { text-align: center; }
                            img { max-width: 60vw; width: 100%; height: auto; border: 2px solid #333; margin: 0 auto; display: block; }
                            .info { color: white; margin: 10px 0; font-family: Arial, sans-serif; }
                            .controls {
                                display: flex;
                                align-items: center;
                                gap: 20px;
                                margin: 20px 0;
                                flex-wrap: wrap;
                            }
                            .button-group {
                                display: contents;
                            }
                            .checkbox-container {
                                display: flex; align-items: center; margin: 0;
                            }
                            button { margin: 5px; padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                            button:hover { background: #0056b3; }
                            .calibration-info { background: #333; padding: 15px; border-radius: 10px; margin: 20px 0; }
                            .refresh-rate { color: #00ff00; font-weight: bold; }
                            .refresh-rate.disabled { text-decoration: line-through; color: #888; }
                            .checkbox-container input[type=\"checkbox\"] { opacity: 0; width: 0; height: 0; position: absolute; }
                            .checkbox-container label {
                                display: inline-flex;
                                align-items: center;
                                cursor: pointer;
                                font-size: 16px;
                                color: white;
                                user-select: none;
                                position: relative;
                                padding-left: 32px;
                                margin-bottom: 0;
                            }
                            .checkbox-container .checkmark {
                                position: absolute;
                                left: 0;
                                top: 50%;
                                transform: translateY(-50%);
                                height: 22px;
                                width: 22px;
                                background-color: #222;
                                border: 2px solid #007bff;
                                border-radius: 4px;
                                transition: background 0.2s, border 0.2s;
                            }
                            .checkbox-container label:hover .checkmark {
                                border-color: #0056b3;
                                background: #333;
                            }
                            .checkbox-container input[type=\"checkbox\"]:checked + label .checkmark {
                                background-color: #007bff;
                                border-color: #007bff;
                            }
                            .checkbox-container .checkmark:after {
                                content: "";
                                position: absolute;
                                display: none;
                                left: 6px;
                                top: 2px;
                                width: 6px;
                                height: 12px;
                                border: solid white;
                                border-width: 0 3px 3px 0;
                                transform: rotate(45deg);
                            }
                            .checkbox-container input[type=\"checkbox\"]:checked + label .checkmark:after {
                                display: block;
                            }
                        </style>
                    </head>
                    <body>
                        <div class=\"container\">\n                            <div class=\"info\">\n                                <h2>Camera Stream - Calibration Mode</h2>\n                                <div class=\"calibration-info\">\n                                    <p>Resolution: """ + f"{streamer.calibration_width}x{streamer.calibration_height}" + """ | FPS: """ + str(streamer.calibration_fps) + """</p>\n                                    <p class=\"refresh-rate\" id=\"refreshRate\">Auto-refresh: Every 1 second</p>\n                                    <p>JPEG Quality: """ + str(streamer.stream_quality) + """%</p>\n                                </div>\n                            </div>\n                            <img id=\"stream\" src=\"/stream\" alt=\"Camera Stream\">\n                            <div class=\"controls\">\n                                <div class=\"checkbox-container\">\n                                    <input type=\"checkbox\" id=\"autoRefreshCheckbox\" checked>\n                                    <label for=\"autoRefreshCheckbox\">Auto-refresh stream<span class=\"checkmark\"></span></label>\n                                </div>\n                                <button onclick=\"location.reload()\">Refresh Page</button>\n                                <button onclick=\"document.getElementById('stream').src='/stream?' + new Date().getTime()\">Reload Stream</button>\n                            </div>\n                        </div>\n                        <script>\n                            let autoRefreshEnabled = true;\n                            let refreshInterval;\n                            \n                            function handleAutoRefreshChange() {\n                                const checkbox = document.getElementById('autoRefreshCheckbox');\n                                autoRefreshEnabled = checkbox.checked;\n                                \n                                if (autoRefreshEnabled) {\n                                    startAutoRefresh();\n                                    document.getElementById('refreshRate').classList.remove('disabled');\n                                    console.log('Auto-refresh enabled');\n                                } else {\n                                    clearInterval(refreshInterval);\n                                    document.getElementById('refreshRate').classList.add('disabled');\n                                    console.log('Auto-refresh disabled');\n                                }\n                            }\n                            \n                            function startAutoRefresh() {\n                                refreshInterval = setInterval(function() {\n                                    if (autoRefreshEnabled) {\n                                        document.getElementById('stream').src = '/stream?' + new Date().getTime();\n                                    }\n                                }, 1000); // Refresh every 1 second for calibration\n                            }\n                            \n                            // Start auto-refresh immediately\n                            startAutoRefresh();\n                            \n                            // Add event listener to checkbox\n                            document.addEventListener('DOMContentLoaded', function() {\n                                document.getElementById('autoRefreshCheckbox').addEventListener('change', handleAutoRefreshChange);\n                            });\n                            \n                            // Also refresh on page load\n                            window.onload = function() {\n                                document.getElementById('stream').src = '/stream?' + new Date().getTime();\n                            };\n                        </script>\n                    </body>\n                    </html>\n                    """
                    self.wfile.write(html.encode())

                elif self.path.startswith('/stream'):
                    print("[DEBUG] /stream endpoint hit")
                    with streamer.frame_lock:
                        if streamer.current_frame is not None:
                            print("[DEBUG] Frame available, sending JPEG")
                            # Encode as JPEG with higher quality for calibration
                            _, buffer = cv2.imencode('.jpg', streamer.current_frame, [cv2.IMWRITE_JPEG_QUALITY, streamer.stream_quality])
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