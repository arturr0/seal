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
    const frameInterval = 100;

    async function processFrame(timestamp) {
        // ... (your existing code)
    }

    animationFrameId = requestAnimationFrame(processFrame);

    return () => {
        cancelAnimationFrame(animationFrameId);
        if (processedSrc) URL.revokeObjectURL(processedSrc);
    };
}, [processedSrc]); // ✅ Now includes `processedSrc`

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
