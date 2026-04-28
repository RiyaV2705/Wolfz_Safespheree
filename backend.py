import cv2
from ultralytics import YOLO
from collections import deque
from datetime import datetime
import numpy as np

# Load YOLO model
model = YOLO("yolov8n.pt")

# Tracking memory
track_history = {}
unique_ids = set()

# Danger tracking
danger_times = []
last_logged_minute = None

# Heatmap points
heatmap_points = deque(maxlen=500)

def process_frame(frame):
    global last_logged_minute

    results = model(frame)[0]

    count = 0
    new_ids = set()

    for box in results.boxes:
        cls = int(box.cls[0])

        if cls == 0:  # person
            count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            heatmap_points.append((cx, cy))

            matched = False

            for uid, (px, py) in track_history.items():
                if abs(cx - px) < 50 and abs(cy - py) < 50:
                    track_history[uid] = (cx, cy)
                    new_ids.add(uid)
                    matched = True
                    break

            if not matched:
                new_id = len(track_history) + 1
                track_history[new_id] = (cx, cy)
                new_ids.add(new_id)
                unique_ids.add(new_id)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    status = "SAFE" if count <= 3 else "DANGEROUS"

    current_minute = datetime.now().strftime("%H:%M")
    if status == "DANGEROUS":
        if last_logged_minute != current_minute:
            danger_times.append(current_minute)
            last_logged_minute = current_minute

    #  Heatmap
    heatmap = np.zeros_like(frame, dtype=np.uint8)
    for (x, y) in heatmap_points:
        cv2.circle(heatmap, (x, y), 20, (0, 0, 255), -1)

    heatmap = cv2.GaussianBlur(heatmap, (25, 25), 0)
    frame = cv2.addWeighted(frame, 0.7, heatmap, 0.3, 0)

    return frame, count, status, len(unique_ids), danger_times
