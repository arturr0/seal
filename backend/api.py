import cv2
import numpy as np
from pyvpd import VPDetector
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

def generate_frames():
    cap = cv2.VideoCapture(0)
    vp_detector = VPDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect vanishing points
        vps_3d, vps_2d = vp_detector.detect(frame)

        if vps_2d is not None and len(vps_2d) > 0:
            principal_point = np.array([frame.shape[1] / 2, frame.shape[0] / 2])

            # Get first vanishing point and reduce to 2D if needed
            vp_point = np.array(vps_2d[0])
            if vp_point.shape[0] >= 2:
                vp_point_2d = vp_point[:2]
                try:
                    focal_length = np.linalg.norm(vp_point_2d - principal_point)
                    # Annotate the frame with focal length
                    cv2.putText(frame, f"Focal Length: {focal_length:.2f} px", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                except Exception as e:
                    # Just skip annotation if something unexpected happens
                    print(f"Warning: failed to calculate focal length: {e}")
            else:
                print("Warning: vanishing point does not have enough dimensions")

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        # Yield frame in multipart format
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
