import React, { useState, useRef } from 'react';

export default function UploadStep({ onUpload }) {
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState('');
  const [file, setFile] = useState(null);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith('.csv')) {
      alert('El archivo debe ser .csv');
      return;
    }
    setFile(f);
    setFileName(f.name);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = () => {
    if (file) onUpload(file);
  };

  return (
    <div className="card">
      <h2>Subí tu CSV de URLs</h2>
      <p className="subtitle">
        La primera columna debe contener las URLs de YouTube (videos y/o Shorts).
        El nombre de la columna puede ser cualquiera.
      </p>

      <div
        className={`dropzone ${dragging ? 'dragging' : ''} ${fileName ? 'has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {fileName ? (
          <>
            <span className="drop-icon">📄</span>
            <span className="drop-filename">{fileName}</span>
            <span className="drop-hint">Hacé clic para cambiar el archivo</span>
          </>
        ) : (
          <>
            <span className="drop-icon">📂</span>
            <span className="drop-label">Arrastrá tu CSV acá</span>
            <span className="drop-hint">o hacé clic para buscar</span>
          </>
        )}
      </div>

      <div className="info-grid">
        <div className="info-item">
          <span className="info-icon">📥</span>
          <div>
            <strong>Entrada</strong>
            <p>CSV con URLs de YouTube en la columna A</p>
          </div>
        </div>
        <div className="info-item">
          <span className="info-icon">📤</span>
          <div>
            <strong>Salida</strong>
            <p>CSV con 13 columnas: canal, vistas, likes, fecha, tags…</p>
          </div>
        </div>
        <div className="info-item">
          <span className="info-icon">⚡</span>
          <div>
            <strong>Velocidad</strong>
            <p>~2–4 seg por URL. 200 URLs ≈ 10 min</p>
          </div>
        </div>
        <div className="info-item">
          <span className="info-icon">🎬</span>
          <div>
            <strong>Tipos</strong>
            <p>Videos normales y YouTube Shorts</p>
          </div>
        </div>
      </div>

      <button
        className="btn-primary"
        disabled={!file}
        onClick={handleSubmit}
      >
        Iniciar crawling →
      </button>
    </div>
  );
}
