import { useState, useEffect } from 'react';

const useCalibration = () => {
    const [focalLength, setFocalLength] = useState(null);

    useEffect(() => {
        const interval = setInterval(() => {
            fetch('/api/focal-length')
                .then(response => response.json())
                .then(data => setFocalLength(data.focalLength))
                .catch(error => console.error('Error fetching focal length:', error));
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    return focalLength;
};

export default useCalibration;
