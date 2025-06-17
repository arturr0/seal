// src/api/api.js

export const getFocalLength = async () => {
    try {
        const response = await fetch('/api/focal-length');
        const data = await response.json();
        return data.focalLength;
    } catch (error) {
        console.error('Error fetching focal length:', error);
        return null;
    }
};
