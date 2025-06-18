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

            // Calculate time difference since last frame
            const timeDiff = timestamp - lastTimestamp;
            
            if (timeDiff < frameInterval) {
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

                    const response = await fetch("https://seal-80a2.onrender.com/process_frame", {
                        method: "POST",
                        body: formData,
                        headers: {
                            'Accept': 'image/jpeg',
                        },
                        mode: 'cors',
                    });

                    if (response.ok) {
                        const blobProcessed = await response.blob();
                        const url = URL.createObjectURL(blobProcessed);

                        setProcessedSrc((oldUrl) => {
                            console.log('Setting processedSrc:', url);
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
    }, [processedSrc]); // Added processedSrc to dependencies

    return (
        <div>
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
