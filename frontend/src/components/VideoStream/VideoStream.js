// src/components/VideoStream/VideoStream.js

import React, { useEffect, useState } from 'react';
import { getFocalLength } from '../../api/api';
import './VideoStream.css';

const VideoStream = () => {
    const [focalLength, setFocalLength] = useState(null);

    useEffect(() => {
        const interval = setInterval(() => {
            getFocalLength().then(setFocalLength);
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="video-container">
            <h1>Live Video Stream</h1>
            <img src="https://seal-80a2.onrender.com/process_frame alt="Live Video Stream" />
            {focalLength && <p>Focal Length: {focalLength.toFixed(2)} px</p>}
        </div>
    );
};

export default VideoStream;
