from src.deepseek_client import DeepseekClient
import logging
import json
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def call_api_with_retry(client: DeepseekClient, messages: list, description: str, retries: int = 3) -> str:
    """
    Realiza una llamada a la API con reintentos y delays.
    """
    for attempt in range(retries):
        try:
            # Agregar delay entre intentos
            if attempt > 0:
                time.sleep(5 * (attempt + 1))  # Backoff exponencial: 5s, 10s, 15s
            
            logger.info(f"Intento {attempt + 1} de {retries} para {description}")
            response = client.chat(
                messages=messages,
                model="deepseek-reasoner",
                temperature=0.2
            )
            
            # Validar la respuesta
            if not response or "choices" not in response:
                raise ValueError("Respuesta inválida de la API")
                
            content = response["choices"][0]["message"]["content"]
            if not content.strip():
                raise ValueError("La API retornó una respuesta vacía")
                
            return content
            
        except Exception as e:
            logger.error(f"Error en intento {attempt + 1} para {description}: {str(e)}")
            if attempt == retries - 1:  # Último intento
                raise
    
    return None

def get_initial_structure():
    """
    Solicita a Deepseek la estructura inicial del proyecto.
    """
    client = DeepseekClient()
    
    messages = [
        {
            "role": "system",
            "content": "Generate only Python code with basic types and docstrings."
        },
        {
            "role": "user",
            "content": """
            Create a Python class structure for a real estate scraper:
            
            1. RealEstateScraper class with:
               - Search parameters (location, property type, sources)
               - Basic scraping methods
               - Error handling
            
            Keep it simple, focus on structure.
            """
        }
    ]
    
    return call_api_with_retry(client, messages, "estructura inicial")

def get_data_processing_functions():
    """
    Solicita a Deepseek las funciones de procesamiento de datos.
    """
    client = DeepseekClient()
    
    messages = [
        {
            "role": "system",
            "content": "Generate only Python code with basic types and docstrings."
        },
        {
            "role": "user",
            "content": """
            Create these data processing functions:
            
            def limpiar_precio(texto: str) -> float:
                '''Clean and convert price text to float'''
            
            def calcular_m2(texto: str) -> int:
                '''Extract and convert area to integer'''
            
            def geocodificar(direccion: str) -> tuple[float, float]:
                '''Convert address to coordinates'''
            """
        }
    ]
    
    return call_api_with_retry(client, messages, "funciones de procesamiento")

def get_visualization_code():
    """
    Solicita a Deepseek el código base para visualizaciones.
    """
    client = DeepseekClient()
    
    messages = [
        {
            "role": "system",
            "content": "Generate only Python code with basic types and docstrings."
        },
        {
            "role": "user",
            "content": """
            Create visualization functions:
            
            1. create_heatmap(data, location) using folium
            2. plot_price_histogram(prices) using matplotlib
            3. plot_scatter(x, y, data) using seaborn
            
            Basic structure only.
            """
        }
    ]
    
    return call_api_with_retry(client, messages, "código de visualización")

def main():
    """
    Función principal que ejecuta las pruebas de generación de código.
    """
    logger.info("Iniciando generación de estructura del proyecto...")
    
    # Parámetros de búsqueda
    search_params = {
        "ubicacion": "Hipódromo Condesa, CDMX",
        "tipo_inmueble": "Consultorio médico",
        "fuentes": ["Inmuebles24", "Properati", "Vivanuncios"],
        "terminos": ["consultorio renta", "espacio médico", "subarriendo clínica"]
    }
    
    try:
        # Generar y guardar estructura inicial
        estructura = get_initial_structure()
        if estructura:
            with open("real_estate_structure.py", "w", encoding="utf-8") as f:
                f.write(estructura)
            logger.info("Estructura base generada y guardada")
        
        # Pequeño delay entre llamadas
        time.sleep(5)
        
        # Generar y guardar funciones de procesamiento
        funciones = get_data_processing_functions()
        if funciones:
            with open("data_processing.py", "w", encoding="utf-8") as f:
                f.write(funciones)
            logger.info("Funciones de procesamiento generadas y guardadas")
        
        # Pequeño delay entre llamadas
        time.sleep(5)
        
        # Generar y guardar código de visualización
        visualizaciones = get_visualization_code()
        if visualizaciones:
            with open("visualizations.py", "w", encoding="utf-8") as f:
                f.write(visualizaciones)
            logger.info("Código de visualización generado y guardado")
        
        # Guardar parámetros de búsqueda
        with open("search_params.json", "w", encoding="utf-8") as f:
            json.dump(search_params, f, indent=4, ensure_ascii=False)
        logger.info("Parámetros de búsqueda guardados")
        
    except Exception as e:
        logger.error(f"Error en la generación de código: {str(e)}")
        raise

if __name__ == "__main__":
    main()