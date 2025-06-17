from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
import os
from flask_cors import CORS
from waitress import serve

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)
@app.route('/service-worker.js')
def sw():
    return send_from_directory(
        os.path.abspath(os.path.join(__file__, '..', '../frontend/build')),
        'service-worker.js'
    )



@app.route('/api/measure', methods=['POST'])
def measure():
    file = request.files['image']
    arr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)
    (_, _), (MA, ma), angle = cv2.fitEllipse(c)
    # Assuming 10px = 1mm calibration
    result = {
        'major_axis_mm': round(MA * 0.1, 2),
        'minor_axis_mm': round(ma * 0.1, 2),
        'angle_deg': round(angle, 2)
    }
    return jsonify(result)

# Serve React build
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Default to 5000 if PORT is not set
    serve(app, host='0.0.0.0', port=port)
