import React, { useRef, useEffect, useState } from "react";

function WebcamProcessor() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [processedSrc, setProcessedSrc] = useState(null);

    useEffect(() => {
        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            } catch (err) {
                console.error("Error accessing webcam", err);
            }
        }
        setupCamera();
    }, []);

    useEffect(() => {
        let animationFrameId;
        let lastTimestamp = 0;
        const frameInterval = 100; // approx 10 fps

        async function processFrame(timestamp) {
            if (!videoRef.current || !canvasRef.current) return;

            if (timestamp - lastTimestamp < frameInterval) {
                animationFrameId = requestAnimationFrame(processFrame);
                return;
            }
            lastTimestamp = timestamp;

            const video = videoRef.current;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext("2d");

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(async (blob) => {
                if (!blob) return;

                try {
                    const formData = new FormData();
                    formData.append("frame", blob, "frame.jpg");

                    const response = await fetch("http://localhost:5000/process_frame", {
                        method: "POST",  // Ensure POST is used
                        body: formData,
                        headers: {
                            // Explicitly set headers (optional but helpful)
                            'Accept': 'image/jpeg',
                        },
                        mode: 'cors',  // Ensure CORS mode
                    });


                    if (response.ok) {
                        const blobProcessed = await response.blob();
                        const url = URL.createObjectURL(blobProcessed);

                        setProcessedSrc((oldUrl) => {
                            console.log('Setting processedSrc:', url); // Debug log

                            if (oldUrl) URL.revokeObjectURL(oldUrl);
                            return url;
                        });
                    } else {
                        console.error("Error processing frame:", response.statusText);
                    }
                } catch (err) {
                    console.error("Fetch error:", err);
                }
            }, "image/jpeg");

            animationFrameId = requestAnimationFrame(processFrame);
        }

        animationFrameId = requestAnimationFrame(processFrame);

        return () => {
            cancelAnimationFrame(animationFrameId);
            if (processedSrc) URL.revokeObjectURL(processedSrc);
        };
    }, []);

    return (
        <div>
            {/* Hidden video and canvas for processing */}
            <video ref={videoRef} style={{ display: "none" }} playsInline />
            <canvas ref={canvasRef} style={{ display: "none" }} />
            {processedSrc ? (
                <img
                    src={processedSrc}
                    alt="Processed webcam feed"
                    style={{ maxWidth: "100%", border: "2px solid #333" }}
                />
            ) : (
                <p>Loading webcam feed...</p>
            )}
        </div>
    );
}

export default WebcamProcessor;
