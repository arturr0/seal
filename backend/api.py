import os
import cv2
import numpy as np
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/process_frame": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
}, supports_credentials=True)

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
                circles = np.concatenate((circles, detected), axis=1)

    if circles is not None and circles.shape[1] > 0:
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            mask = np.zeros_like(gray)
            cv2.circle(mask, center, radius, 255, -1)
            masked = cv2.bitwise_and(gray, gray, mask=mask)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0:
                    continue
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if 0.85 <= circularity <= 1.15:
                    cv2.circle(frame, center, radius, (0, 255, 0), 2)
                    cv2.circle(frame, center, 2, (0, 0, 255), 3)

    return frame

@app.route('/')
def home():
    return "Circle Detection API is running. Use /process_frame endpoint for image processing."

@app.route('/process_frame', methods=['POST', 'OPTIONS'])
def process_frame():
    if request.method not in ['POST', 'OPTIONS']:
        response = Response(
            response="Method Not Allowed",
            status=405,
            mimetype='text/plain'
        )
        response.headers['Allow'] = 'POST, OPTIONS'
        return response

    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    if 'frame' not in request.files:
        return 'No frame received', 400

    file = request.files['frame']
    try:
        img_bytes = file.read()
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is None:
            return 'Failed to decode image', 400

        processed_frame = detect_oring(frame)
        _, buffer = cv2.imencode('.jpg', processed_frame)

        response = Response(buffer.tobytes(), mimetype='image/jpeg')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        app.logger.error(f"Error processing frame: {str(e)}")
        return 'Internal server error', 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Disable debug mode in production
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host='0.0.0.0', port=port, debug=debug)
