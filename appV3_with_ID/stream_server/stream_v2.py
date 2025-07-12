      # camera_server.py (on Pi with camera)
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from picamera2 import Picamera2
import cv2
import threading
import time
import io
import numpy as np

app = FastAPI()

# Allow requests from any frontend (use specific IPs in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(1)

state = {
    "zoom": 1.0,
    "hflip": False,
    "vflip": False,
    "brightness": 50
}

@app.get("/stream")
def stream():
    def generate():
        while True:
            frame = picam2.capture_array()
            # Apply horizontal flip
            if state["hflip"]:
                frame = cv2.flip(frame, 1)
            if state["vflip"]:
                frame = cv2.flip(frame, 0)

            # Resize or zoom crop logic
            if state["zoom"] > 1.0:
                h, w = frame.shape[:2]
                z = state["zoom"]
                new_w, new_h = int(w/z), int(h/z)
                x1, y1 = (w - new_w)//2, (h - new_h)//2
                frame = frame[y1:y1+new_h, x1:x1+new_w]
                frame = cv2.resize(frame, (w, h))

            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            time.sleep(0.03)

    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/zoom")
async def set_zoom(request: Request):
    data = await request.json()
    state["zoom"] = float(data.get("level", 1.0))
    return JSONResponse({"status": "ok", "zoom": state["zoom"]})

@app.post("/flip")
async def set_flip(request: Request):
    data = await request.json()
    state["hflip"] = bool(data.get("horizontal", False))
    state["vflip"] = bool(data.get("vertical", False))
    return JSONResponse({"status": "ok", "hflip": state["hflip"], "vflip": state["vflip"]})

@app.post("/brightness")
async def set_brightness(request: Request):
    data = await request.json()
    brightness = int(data.get("value", 50))
    state["brightness"] = brightness
    picam2.set_controls({"Brightness": float(brightness)})
    return JSONResponse({"status": "ok", "brightness": brightness})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
