/* src/service-worker.js */
import { precacheAndRoute } from 'workbox-precaching';

/* eslint-disable no-restricted-globals */
precacheAndRoute(self.__WB_MANIFEST);

// Optional: Listen for 'install' or other lifecycle events
self.addEventListener('install', event => {
    // your custom logic here, e.g., skipWaiting or cleanup
});
