import React from "react";
import WebcamProcessor from "./components/WebcamProcessor";

function App() {
  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>Webcam Circle Detection</h1>
      <WebcamProcessor />
    </div>
  );
}

export default App;
