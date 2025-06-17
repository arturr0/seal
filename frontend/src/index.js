import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import * as serviceWorkerRegistration from './serviceWorkerRegistration';

const container = document.getElementById('root');
const root = createRoot(container);         // create a React 18 root
root.render(                                // then render your app
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Register service worker
serviceWorkerRegistration.register();
