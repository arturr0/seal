import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [res, setRes] = useState(null);

  const upload = async () => {
    const fd = new FormData();
    fd.append('image', file);
    const resp = await fetch('/api/measure', { method: 'POST', body: fd });
    setRes(await resp.json());
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>O‑Ring Measurement App</h1>
      <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
      <button onClick={upload} disabled={!file}>Measure</button>
      {res && (
        <div>
          <p>Major axis: {res.major_axis_mm} mm</p>
          <p>Minor axis: {res.minor_axis_mm} mm</p>
          <p>Angle: {res.angle_deg}°</p>
        </div>
      )}
    </div>
  );
}

export default App;
