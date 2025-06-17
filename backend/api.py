import cv2
import numpy as np
from pyvpd import VPDetector
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS
def detect_oring(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                               param1=50, param2=30, minRadius=10, maxRadius=200)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        # Take the first detected circle (or iterate all)
        for i in circles[0, :1]:
            center = (i[0], i[1])
            radius = i[2]

            # Draw the circle and center on the frame
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.circle(frame, center, 2, (0, 0, 255), 3)

            # Return radius in pixels
            return radius, frame

    return None, frame
def generate_frames():
    cap = cv2.VideoCapture(0)
    vp_detector = VPDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        radius, annotated_frame = detect_oring(frame)

        if radius:
            cv2.putText(annotated_frame, f"Radius: {radius} px", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            annotated_frame = frame

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
    focal_length = 142.35
    return jsonify({'focalLength': focal_length})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
