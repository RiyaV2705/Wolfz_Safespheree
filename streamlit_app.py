import streamlit as st
import cv2
from backend import process_frame
import tempfile
import time
from datetime import datetime
import subprocess
import threading
import os

#  Alarm (Mac safe)
def play_alarm():
    try:
        subprocess.run(["afplay", "alarm.wav"])
    except:
        pass

st.set_page_config(layout="wide")
st.title(" SafeSphere - AI Crowd Monitoring System")

# Sidebar
source = st.sidebar.radio("Input Source", ["Webcam", "Upload Video"])

video_file = None
if source == "Upload Video":
    video_file = st.sidebar.file_uploader("Upload Video", type=["mp4", "avi"])

start = st.sidebar.button("Start Monitoring")

# UI
frame_window = st.image([])
graph = st.line_chart([])
count_text = st.empty()
status_text = st.empty()
unique_text = st.empty()
danger_placeholder = st.empty()
alert_placeholder = st.empty()

count_history = []
frame_count = 0
last_alert_minute = None

if not os.path.exists("alarm.wav"):
    st.warning("⚠ alarm.wav not found")

#  START
if start:

    if source == "Webcam":
        cap = cv2.VideoCapture(0)
    else:
        if video_file is None:
            st.warning("Upload a video first")
            st.stop()

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        cap = cv2.VideoCapture(tfile.name)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.success(" Video finished")
            break

        frame_count += 1

        if frame_count % 2 != 0:
            continue

        #  AUTO ROTATION FIX (tries all and picks best)
        if source == "Upload Video":
            rotations = [
                frame,
                cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE),
                cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE),
                cv2.rotate(frame, cv2.ROTATE_180),
            ]

            best_frame = frame
            max_people = 0

            for test_frame in rotations:
                temp_frame, temp_count, _, _, _ = process_frame(test_frame.copy())
                if temp_count > max_people:
                    max_people = temp_count
                    best_frame = test_frame

            frame = best_frame

        # Webcam mirror
        if source == "Webcam":
            frame = cv2.flip(frame, 1)

        # Resize
        frame = cv2.resize(frame, (640, 480))

        # Process
        processed_frame, count, status, unique_count, danger_times = process_frame(frame)

        # Display
        frame_window.image(processed_frame, channels="BGR")

        count_text.markdown(f"###  Current Count: {count}")

        if status == "SAFE":
            status_text.markdown(f"###  Status: {status}")
        else:
            status_text.markdown(f"###  Status: {status}")

        unique_text.markdown(f"###  Unique People: {unique_count}")

        count_history.append(count)
        graph.line_chart(count_history)

        danger_placeholder.markdown("###  Dangerous Times")

        if danger_times:
            danger_placeholder.markdown(
                "\n".join([f" {t}" for t in danger_times[-5:]])
            )
        else:
            danger_placeholder.write("No dangerous events yet")

        #  ALERT
        current_minute = datetime.now().strftime("%H:%M")

        if status == "DANGEROUS":
            alert_placeholder.warning(" Area is overcrowded")

            if last_alert_minute != current_minute:
                alert_placeholder.error(" OVERCROWDING DETECTED!")
                threading.Thread(target=play_alarm, daemon=True).start()
                last_alert_minute = current_minute
        else:
            alert_placeholder.empty()

        time.sleep(0.01)

# Footer
st.markdown("---")
st.markdown("### ⚡ Features")
st.write("- Real-time detection")
st.write("- Person tracking")
st.write("- Heatmap")
st.write("- Video + Webcam support")
st.write("- Smart alert system")
