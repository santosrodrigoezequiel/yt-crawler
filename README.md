# 🎬 YouTube SEO Crawler

Extrae métricas SEO de videos y Shorts de YouTube a partir de un CSV de URLs.

## Arquitectura

```
frontend/   → React app → Vercel
backend/    → FastAPI   → Railway
```

---

## Deploy paso a paso

### 1. Backend en Railway

1. Creá cuenta en [railway.app](https://railway.app)
2. Nuevo proyecto → **Deploy from GitHub repo**
3. Seleccioná tu repo y como **Root Directory** elegí `backend/`
4. Railway detecta automáticamente el `Procfile` y usa `requirements.txt`
5. Una vez deployado, copiá la URL pública (ej: `https://yt-crawler-production.railway.app`)

### 2. Frontend en Vercel

1. Creá cuenta en [vercel.com](https://vercel.com)
2. Nuevo proyecto → importá tu repo de GitHub
3. En **Root Directory** elegí `frontend/`
4. En **Environment Variables** agregá:
   ```
   REACT_APP_API_URL = https://TU-PROYECTO.railway.app
   ```
   (la URL que copiaste en el paso anterior)
5. Deploy → Vercel genera tu URL pública

### 3. Actualizar CORS en el backend (opcional pero recomendado)

En `backend/main.py`, reemplazá `allow_origins=["*"]` por tu dominio de Vercel:

```python
allow_origins=["https://tu-proyecto.vercel.app"]
```

---

## Uso

1. Abrí la app en Vercel
2. Subí tu CSV (primera columna = URLs de YouTube)
3. Esperá el progreso en tiempo real
4. Descargá el CSV con los datos SEO

## Columnas del CSV de salida

| Col | Campo | Descripción |
|-----|-------|-------------|
| A | Landing_page | URL original |
| B | Nombre_canal | Canal de YouTube |
| C | Visualizaciones | Vistas (videos y shorts) |
| D | Likes | Likes (shorts) |
| E | Fecha_publicacion | Fecha de publicación |
| F | Titulo | Título del video |
| G | Duracion | Duración (MM:SS o HH:MM:SS) |
| H | Comentarios | Cantidad de comentarios |
| I | Hashtags | Hashtags del video |
| J | Thumbnail_url | URL de la miniatura |
| K | Tags | Keywords/tags del video |
| L | Tipo | `video` o `short` |
| M | Error | Detalle de error si falló |

## Desarrollo local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```
