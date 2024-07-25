#!/usr/bin/python3

# server.py

import io
import logging
import socketserver
from http import server
from threading import Condition
import libcamera
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    zoom_count = 0
    hflip=0
    vflip=0

    def do_GET(self):
        # For Endpoint and functions
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            with open('index.html', 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/zoom':
            # Function for zooming
            size = picam2.capture_metadata()['ScalerCrop'][2:]
            full_res = picam2.camera_properties['PixelArraySize']
            for _ in range(10):
                # This syncs us to the arrival of a new camera frame:
                size = [int(s * 0.95) for s in size]
                offset = [(r - s) // 2 for r, s in zip(full_res, size)]
                picam2.set_controls({"ScalerCrop": offset + size})
                print(offset+size)
            self.send_response(200)
            self.end_headers()
        elif self.path == '/reset_view':
            #Gets executed every fifth press
            initial_scaler_crop = (80,60,2432,1824)
            picam2.set_controls({"ScalerCrop":initial_scaler_crop})
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/rotate_odd_h':
            picam2.stop()
            preview_config["transform"] = libcamera.Transform(hflip=True)
            picam2.configure(preview_config)
            picam2.start()
        elif self.path == '/rotate_even_h':
            picam2.stop()
            preview_config["transform"] = libcamera.Transform(hflip=0, vflip=0)
            picam2.configure(preview_config)
            picam2.start()
        elif self.path == '/rotate_even_v':
            picam2.stop()
            preview_config["transform"] = libcamera.Transform(hflip=0, vflip=0)
            picam2.configure(preview_config)
            picam2.start()
        elif self.path == '/rotate_odd_v':
            picam2.stop()
            preview_config["transform"] = libcamera.Transform(vflip=True)
            picam2.configure(preview_config)
            picam2.start()
        elif self.path == '/refresh_stuff':
            picam2.stop()
            preview_config["transform"] = libcamera.Transform(hflip=0, vflip=0)
            picam2.configure(preview_config)
            picam2.start()
        else:
        # Serve static files(Images)
            try:
                with open('static' + self.path, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                if self.path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
                    self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404)
                self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

picam2 = Picamera2()
preview_config=picam2.create_video_configuration(main={"size": (640, 480) })
picam2.configure(preview_config)
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
