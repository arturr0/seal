import React, { useEffect, useState, useRef } from 'react';
import { getFocalLength } from '../../api/api';
import './VideoStream.css';

const VideoStream = () => {
    const [focalLength, setFocalLength] = useState(null);
    const [processedImage, setProcessedImage] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

   const captureAndProcessFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('frame', blob, 'frame.jpg');

        try {
            const response = await fetch('https://seal-80a2.onrender.com/process_frame', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'image/jpeg'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            setProcessedImage(URL.createObjectURL(blob));
        } catch (error) {
            console.error('Error processing frame:', error);
            setError('Failed to process frame');
        }
    }, 'image/jpeg', 0.95);  // 0.95 = quality
};

    useEffect(() => {
        // Setup camera stream
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
                
                // Process frames every second
                const interval = setInterval(() => {
                    captureAndProcessFrame();
                    getFocalLength().then(setFocalLength);
                }, 1000);

                return () => clearInterval(interval);
            })
            .catch(console.error);

    }, []);

    return (
        <div className="video-container">
            <h1>Live Video Stream</h1>
            
            {/* Hidden video and canvas elements */}
            <video ref={videoRef} style={{display: 'none'}} playsInline />
            <canvas ref={canvasRef} style={{display: 'none'}} width="640" height="480" />
            
            {/* Display processed image */}
            {processedImage && (
                <img src={processedImage} alt="Processed Video Stream" />
            )}
            
            {focalLength && <p>Focal Length: {focalLength.toFixed(2)} px</p>}
        </div>
    );
};

export default VideoStream;
