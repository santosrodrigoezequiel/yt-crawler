"""
YouTube SEO Crawler — API FastAPI
Railway deployment
"""

import io
import uuid
import threading
import csv
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from crawler import procesar_urls, COLUMNAS

app = FastAPI(title="YouTube SEO Crawler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: reemplazar con tu dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Estado en memoria de los jobs ─────────────────────────────────────────────
jobs: dict[str, dict] = {}


def _detectar_separador(contenido: str) -> str:
    primera_linea = contenido.splitlines()[0] if contenido else ""
    candidatos = {
        ",": primera_linea.count(","),
        ";": primera_linea.count(";"),
        "\t": primera_linea.count("\t"),
        "|": primera_linea.count("|"),
    }
    sep = max(candidatos, key=candidatos.get)
    return sep if candidatos[sep] > 0 else ","


def _extraer_urls(contenido: str) -> list[str]:
    sep = _detectar_separador(contenido)
    df = pd.read_csv(io.StringIO(contenido), sep=sep, dtype=str)
    primera_col = df.columns[0]
    urls = (
        df[primera_col]
        .dropna()
        .str.strip()
        .loc[lambda s: s.str.startswith("http")]
        .tolist()
    )
    return urls


def _run_job(job_id: str, urls: list[str]):
    """Corre el crawling en un thread separado y actualiza el estado."""
    jobs[job_id]["status"] = "running"
    jobs[job_id]["total"] = len(urls)
    jobs[job_id]["current"] = 0
    jobs[job_id]["resultados"] = []

    def on_progress(current, total, dato):
        jobs[job_id]["current"] = current
        jobs[job_id]["ultimo"] = {
            "url": dato.get("Landing_page", ""),
            "canal": dato.get("Nombre_canal", ""),
            "titulo": dato.get("Titulo", "")[:60],
            "tipo": dato.get("Tipo", ""),
        }

    try:
        resultados = procesar_urls(urls, progress_callback=on_progress)
        jobs[job_id]["resultados"] = resultados
        jobs[job_id]["status"] = "done"
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "YouTube SEO Crawler API"}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Recibe un CSV, crea un job y empieza el crawling en background."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "El archivo debe ser .csv")

    contenido = (await file.read()).decode("utf-8-sig", errors="ignore")

    try:
        urls = _extraer_urls(contenido)
    except Exception as e:
        raise HTTPException(400, f"Error leyendo CSV: {e}")

    if not urls:
        raise HTTPException(400, "No se encontraron URLs válidas en la primera columna.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "total": len(urls),
        "current": 0,
        "resultados": [],
        "ultimo": {},
        "created_at": datetime.utcnow().isoformat(),
    }

    thread = threading.Thread(target=_run_job, args=(job_id, urls), daemon=True)
    thread.start()

    return {
        "job_id": job_id,
        "total_urls": len(urls),
        "message": f"Job iniciado con {len(urls)} URLs",
    }


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Devuelve el progreso del job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job no encontrado")

    job = jobs[job_id]
    pct = round((job["current"] / job["total"]) * 100, 1) if job["total"] else 0

    return {
        "job_id": job_id,
        "status": job["status"],
        "current": job["current"],
        "total": job["total"],
        "porcentaje": pct,
        "ultimo": job.get("ultimo", {}),
        "error": job.get("error", ""),
    }


@app.get("/result/{job_id}")
def get_result(job_id: str):
    """Devuelve el CSV final cuando el job está completo."""
    if job_id not in jobs:
        raise HTTPException(404, "Job no encontrado")

    job = jobs[job_id]
    if job["status"] != "done":
        raise HTTPException(400, f"Job no completado (estado: {job['status']})")

    resultados = job["resultados"]
    df = pd.DataFrame(resultados)
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNAS]

    output = io.StringIO()
    df.to_csv(output, index=False, sep=",", encoding="utf-8-sig")
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=youtube_seo_{job_id[:8]}.csv"},
    )


@app.delete("/job/{job_id}")
def delete_job(job_id: str):
    """Limpia un job de la memoria."""
    if job_id in jobs:
        del jobs[job_id]
    return {"deleted": job_id}
