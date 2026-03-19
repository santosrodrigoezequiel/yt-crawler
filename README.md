# 🎬 YouTube | URL Crawler

Extrae métricas SEO de videos y Shorts de YouTube a partir de un CSV de URLs.

## Arquitectura

```
frontend/   → React app → Vercel
backend/    → FastAPI   → Railway
```

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

```
LinkedIn - https://www.linkedin.com/in/santosrodrigoezequiel/
