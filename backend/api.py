import os
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

    circles = None
    radius_ranges = [(10, 40), (30, 90), (80, 150)]

    for min_r, max_r in radius_ranges:
        detected = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=20,
            param1=50,
            param2=35,
            minRadius=min_r,
            maxRadius=max_r
        )
        if detected is not None:
            detected = np.uint16(np.around(detected))
            if circles is None:
                circles = detected
            else:
                # Concatenate along axis=1 (number of circles)
                circles = np.concatenate((circles, detected), axis=1)

    detected_rings = []

    if circles is not None and circles.shape[1] > 0:
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            # Extract small region around circle to compute contour
            mask = np.zeros_like(gray)
            cv2.circle(mask, center, radius, 255, -1)
            masked = cv2.bitwise_and(gray, gray, mask=mask)

            # Find contours in the masked region
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0:
                    continue

                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if 0.85 <= circularity <= 1.15:
                    # Looks circular enough
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

        for (center, radius) in rings:
            cv2.putText(annotated_frame, f"R: {radius}px", (center[0] + 10, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        if annotated_frame is None:
            continue

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
    return jsonify({'focalLength': 142.35})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
