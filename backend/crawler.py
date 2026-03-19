"""
YouTube SEO Crawler — lógica portada del Colab.
Sin Selenium, usa requests + ytInitialData / ytInitialPlayerResponse.
"""

import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DELAY_MIN = 1.5
DELAY_MAX = 3.5

COLUMNAS = [
    "Landing_page", "Nombre_canal", "Visualizaciones", "Likes",
    "Fecha_publicacion", "Titulo", "Duracion", "Comentarios",
    "Hashtags", "Thumbnail_url", "Tags", "Tipo", "Error",
]


def crear_sesion() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-AR,es;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return session


def detectar_tipo(url: str) -> str:
    return "short" if "/shorts/" in url.lower() else "video"


def limpiar(texto) -> str:
    if not texto:
        return ""
    return str(texto).replace("\xa0", " ").strip()


def obtener_html(url: str, session: requests.Session) -> str:
    url = url.replace("m.youtube.com", "www.youtube.com")
    try:
        r = session.get(url, timeout=15)
        return r.text
    except Exception:
        return ""


def _parse_json_by_braces(html: str, marker: str) -> dict:
    """Extrae un JSON de html buscando 'marker' y balanceando llaves."""
    try:
        idx = html.index(marker)
        idx = html.index("{", idx)
        depth, end = 0, idx
        for i, c in enumerate(html[idx:], idx):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        return json.loads(html[idx:end + 1])
    except Exception:
        return {}


def extraer_yt_initial_data(html: str) -> dict:
    return _parse_json_by_braces(html, "ytInitialData")


def extraer_yt_initial_player_response(html: str) -> dict:
    return _parse_json_by_braces(html, "ytInitialPlayerResponse")


def buscar(d, clave):
    """Búsqueda recursiva de clave en dict anidado."""
    if isinstance(d, dict):
        if clave in d:
            return d[clave]
        for v in d.values():
            r = buscar(v, clave)
            if r is not None:
                return r
    elif isinstance(d, list):
        for item in d:
            r = buscar(item, clave)
            if r is not None:
                return r
    return None


def extraer_datos(url: str, session: requests.Session) -> dict:
    tipo = detectar_tipo(url)
    datos = {col: "" for col in COLUMNAS}
    datos["Landing_page"] = url
    datos["Tipo"] = tipo

    html = obtener_html(url, session)
    if not html:
        datos["Error"] = "No se pudo descargar HTML"
        return datos

    soup = BeautifulSoup(html, "html.parser")
    yd = extraer_yt_initial_data(html)
    ypr = extraer_yt_initial_player_response(html)

    # ── Título (fallback desde <title>) ───────────────────────────────────────
    try:
        datos["Titulo"] = limpiar(soup.find("title").text.replace(" - YouTube", ""))
    except Exception:
        pass

    # ── Thumbnail ─────────────────────────────────────────────────────────────
    try:
        og = soup.find("meta", property="og:image")
        if og:
            datos["Thumbnail_url"] = og.get("content", "")
    except Exception:
        pass
    if not datos["Thumbnail_url"]:
        m = re.search(r"(?:v=|/shorts/)([A-Za-z0-9_-]{11})", url)
        if m:
            datos["Thumbnail_url"] = f"https://i.ytimg.com/vi/{m.group(1)}/maxresdefault.jpg"

    # ── ytInitialPlayerResponse → videoDetails ────────────────────────────────
    try:
        vd = ypr.get("videoDetails", {})
        if vd.get("title"):
            datos["Titulo"] = limpiar(vd["title"])
        datos["Nombre_canal"] = limpiar(vd.get("author", ""))
        datos["Visualizaciones"] = limpiar(vd.get("viewCount", ""))
        kw = vd.get("keywords", [])
        if kw:
            datos["Tags"] = ", ".join(kw)
        dur_s = int(vd.get("lengthSeconds", 0))
        if dur_s:
            h, rem = divmod(dur_s, 3600)
            m2, s = divmod(rem, 60)
            datos["Duracion"] = f"{h}:{m2:02d}:{s:02d}" if h else f"{m2}:{s:02d}"
    except Exception:
        pass

    # ── Fecha (videos) desde ytInitialData ────────────────────────────────────
    try:
        fecha = buscar(yd, "dateText")
        if fecha and isinstance(fecha, dict):
            datos["Fecha_publicacion"] = limpiar(fecha.get("simpleText", ""))
    except Exception:
        pass

    # ── Hashtags ──────────────────────────────────────────────────────────────
    try:
        tags = soup.find_all("a", href=re.compile(r"hashtag"))
        datos["Hashtags"] = " | ".join([limpiar(t.text) for t in tags if t.text.strip()])
    except Exception:
        pass

    # ── Shorts: likes, vistas y fecha ─────────────────────────────────────────
    if tipo == "short":
        try:
            mf = ypr.get("microformat", {}).get("playerMicroformatRenderer", {})

            if not datos["Visualizaciones"]:
                datos["Visualizaciones"] = limpiar(mf.get("viewCount", ""))

            try:
                like_title = (
                    yd["overlay"]["reelPlayerOverlayRenderer"]["buttonBar"]
                    ["reelActionBarViewModel"]["buttonViewModels"][0]
                    ["likeButtonViewModel"]["toggleButtonViewModel"]
                    ["toggleButtonViewModel"]["defaultButtonViewModel"]
                    ["buttonViewModel"]["title"]
                )
                datos["Likes"] = limpiar(like_title)
            except (KeyError, IndexError, TypeError):
                pass

            if not datos["Fecha_publicacion"]:
                pub = mf.get("publishDate", "") or mf.get("uploadDate", "")
                if pub:
                    datos["Fecha_publicacion"] = pub[:10]

        except Exception as e:
            datos["Error"] = f"Shorts parse error: {e}"

    return datos


def crawlear_url(url: str, session: requests.Session) -> dict:
    tipo = detectar_tipo(url)
    vacio = {col: "" for col in COLUMNAS}
    vacio["Landing_page"] = url
    vacio["Tipo"] = tipo
    try:
        resultado = extraer_datos(url, session)
        return resultado if resultado is not None else vacio
    except Exception as e:
        vacio["Error"] = str(e)
        return vacio


def procesar_urls(urls: list[str], progress_callback=None) -> list[dict]:
    """
    Procesa una lista de URLs y devuelve lista de dicts.
    progress_callback(current, total, dato) se llama tras cada URL.
    """
    session = crear_sesion()
    resultados = []
    total = len(urls)

    for i, url in enumerate(urls, 1):
        dato = crawlear_url(url.strip(), session)
        resultados.append(dato)

        if progress_callback:
            progress_callback(i, total, dato)

        if i < total:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return resultados
