import React from 'react';

export default function DoneStep({ jobInfo, onDownload, onReset }) {
  const { total, current } = jobInfo;

  return (
    <div className="card card-done">
      <div className="done-icon">✅</div>
      <h2>¡Crawling completado!</h2>
      <p className="subtitle">
        Se procesaron <strong>{current || total}</strong> URLs correctamente.
      </p>

      <div className="done-columns">
        <div className="done-col-label">El CSV incluye:</div>
        <div className="done-cols-grid">
          {[
            ['A', 'Landing_page'],
            ['B', 'Nombre_canal'],
            ['C', 'Visualizaciones'],
            ['D', 'Likes'],
            ['E', 'Fecha_publicacion'],
            ['F', 'Titulo'],
            ['G', 'Duracion'],
            ['H', 'Comentarios'],
            ['I', 'Hashtags'],
            ['J', 'Thumbnail_url'],
            ['K', 'Tags'],
            ['L', 'Tipo'],
            ['M', 'Error'],
          ].map(([col, nombre]) => (
            <div key={col} className="done-col-item">
              <span className="col-letter">{col}</span>
              <span className="col-name">{nombre}</span>
            </div>
          ))}
        </div>
      </div>

      <button className="btn-primary" onClick={onDownload}>
        ⬇️ Descargar CSV
      </button>

      <button className="btn-secondary" onClick={onReset}>
        Procesar otro archivo
      </button>
    </div>
  );
}
