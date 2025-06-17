import cv2
import numpy as np
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def detect_oring(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    gray = cv2.equalizeHist(gray)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=20,
        param1=50,
        param2=35,        # <-- increase this!
        minRadius=20,
        maxRadius=60
    )

    detected_rings = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            if 20 <= radius <= 60:  # filter realistic rings
                cv2.circle(frame, center, radius, (0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 0, 255), 3)
                detected_rings.append((center, radius))

    return detected_rings, frame


def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rings, annotated_frame = detect_oring(frame)

        # Draw radius text for each ring
        for (center, radius) in rings:
            cv2.putText(annotated_frame, f"R: {radius}px", (center[0] + 10, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/focal-length')
def get_focal_length():
    # Placeholder value
    focal_length = 142.35
    return jsonify({'focalLength': focal_length})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
