# Real Estate Scraper

Scraper de rentas de consultorios y oficinas en CDMX, construido con un enfoque experimental:
el módulo generador usa la **API de Deepseek** para producir el andamiaje del proyecto
(estructura del scraper, funciones de procesamiento y visualizaciones), que después se
revisa y ajusta a mano.

## Cómo funciona

El proyecto tiene dos partes:

1. **Generador** (`real_estate_scraper.py`): pide a `deepseek-reasoner` el código base del
   proyecto — la clase del scraper, funciones de limpieza de datos (precio, m², geocodificación)
   y visualizaciones — con reintentos, backoff y logging. Guarda los resultados como módulos
   de Python y los parámetros de búsqueda en `search_params.json`.
2. **Código generado y curado** (`src/`):
   - `real_estate_structure.py` — clase `RealEstateScraper`: parámetros de búsqueda
     (ubicación, tipo de inmueble, fuentes) y métodos de scraping con `requests`.
   - `deepseek_client.py` — cliente de la API de Deepseek (modelos `deepseek-chat` y
     `deepseek-reasoner`) con manejo de errores, reintentos y logging.
   - `visualizations.py` — funciones de visualización de resultados.

La búsqueda objetivo: consultorios médicos en renta en la zona de Hipódromo Condesa,
usando fuentes como Inmuebles24, Properati y Vivanuncios.

## Instalación

```bash
git clone https://github.com/Rodmr092/real_estate_scraper.git
cd real_estate_scraper
python -m venv venv
venv\Scripts\activate      # En Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

## Configuración

El cliente de Deepseek lee la API key de la variable de entorno `DEEPSEEK_API_KEY`:

```bash
set DEEPSEEK_API_KEY=tu-api-key    # En Linux/Mac: export DEEPSEEK_API_KEY=...
```

## Uso

```bash
python real_estate_scraper.py
```

Genera los módulos base del proyecto y guarda los parámetros de búsqueda.

## Estado

Proyecto experimental en pausa. El andamiaje generado funciona; falta conectar el
scraping en vivo contra los portales inmobiliarios.
