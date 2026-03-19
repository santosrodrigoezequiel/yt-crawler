import React from 'react';

export default function ProgressStep({ jobInfo, onCancel }) {
  const { total, current, porcentaje, ultimo } = jobInfo;
  const pct = Math.min(porcentaje || 0, 100);
  const remaining = total - current;
  const estMin = Math.ceil((remaining * 3) / 60); // ~3s por URL

  return (
    <div className="card">
      <h2>Procesando URLs…</h2>
      <p className="subtitle">
        No cerrés esta pestaña. Podés ver el progreso en tiempo real.
      </p>

      <div className="progress-wrap">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="progress-stats">
          <span>{current} / {total} URLs</span>
          <span className="pct-badge">{pct.toFixed(1)}%</span>
        </div>
      </div>

      {remaining > 0 && (
        <p className="eta">
          ⏱ Tiempo estimado restante: ~{estMin} min
        </p>
      )}

      {ultimo?.url && (
        <div className="ultimo-card">
          <div className="ultimo-badge">{ultimo.tipo === 'short' ? '📱 Short' : '🎬 Video'}</div>
          <div className="ultimo-info">
            <span className="ultimo-canal">{ultimo.canal || '—'}</span>
            <span className="ultimo-titulo">{ultimo.titulo || ultimo.url}</span>
          </div>
        </div>
      )}

      <div className="spinner-row">
        <div className="spinner" />
        <span>Crawling en progreso…</span>
      </div>

      <button className="btn-secondary" onClick={onCancel}>
        Cancelar
      </button>
    </div>
  );
}
