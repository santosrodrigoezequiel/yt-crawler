import React, { useState, useRef, useCallback } from 'react';
import UploadStep from './components/UploadStep';
import ProgressStep from './components/ProgressStep';
import DoneStep from './components/DoneStep';
import './App.css';

// ── Configuración ─────────────────────────────────────────────────────────────
// En producción: reemplazar con la URL de tu Railway deployment
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function App() {
  const [step, setStep] = useState('upload'); // upload | progress | done
  const [jobId, setJobId] = useState(null);
  const [jobInfo, setJobInfo] = useState({ total: 0, current: 0, porcentaje: 0, ultimo: {} });
  const [error, setError] = useState('');
  const pollRef = useRef(null);

  const startPolling = useCallback((id) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/status/${id}`);
        const data = await res.json();
        setJobInfo(data);

        if (data.status === 'done') {
          clearInterval(pollRef.current);
          setStep('done');
        } else if (data.status === 'error') {
          clearInterval(pollRef.current);
          setError(data.error || 'Error desconocido en el servidor');
          setStep('upload');
        }
      } catch (e) {
        // Ignorar errores transitorios de red
      }
    }, 2500);
  }, []);

  const handleUpload = useCallback(async (file) => {
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Error al subir el archivo');
        return;
      }

      setJobId(data.job_id);
      setJobInfo({ total: data.total_urls, current: 0, porcentaje: 0, ultimo: {} });
      setStep('progress');
      startPolling(data.job_id);
    } catch (e) {
      setError('No se pudo conectar con el servidor. Verificá que el backend esté activo.');
    }
  }, [startPolling]);

  const handleDownload = useCallback(async () => {
    window.location.href = `${API_BASE}/result/${jobId}`;
  }, [jobId]);

  const handleReset = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (jobId) fetch(`${API_BASE}/job/${jobId}`, { method: 'DELETE' }).catch(() => {});
    setStep('upload');
    setJobId(null);
    setJobInfo({ total: 0, current: 0, porcentaje: 0, ultimo: {} });
    setError('');
  }, [jobId]);

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <span className="logo">🎬</span>
          <div>
<h1>YouTube | URL Crawler</h1>
            <p>Extraé métricas de videos y Shorts a partir de un CSV de URLs</p>
          </div>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="error-banner">
            ⚠️ {error}
            <button onClick={() => setError('')} className="error-close">✕</button>
          </div>
        )}

        {step === 'upload' && <UploadStep onUpload={handleUpload} />}
        {step === 'progress' && <ProgressStep jobInfo={jobInfo} onCancel={handleReset} />}
        {step === 'done' && (
          <DoneStep
            jobInfo={jobInfo}
            onDownload={handleDownload}
            onReset={handleReset}
          />
        )}
      </main>
<footer className="footer">
  <p>
    <a href="https://www.linkedin.com/in/santosrodrigoezequiel/" target="_blank" rel="noreferrer">LinedIn</a>
    {' | Rodrigo Ezequiel Santos'}
  </p>
</footer>
}
