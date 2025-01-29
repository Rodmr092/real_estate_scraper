import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class DeepseekClient:
    '''
    # DeepseekClient

    ## Propósito
    Cliente para interactuar con la API de Deepseek, soportando los modelos
    deepseek-chat y deepseek-reasoner con manejo de errores y logging.

    ## Parámetros
    - api_key (str): API key de Deepseek
    - max_retries (int): Número máximo de reintentos para llamadas a la API
    - timeout (int): Tiempo máximo de espera para respuestas en segundos
    - log_level (int): Nivel de logging (default: logging.INFO)

    ## Ejemplo
    ```python
    client = DeepseekClient(api_key="your-api-key")
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "¿Qué es Python?"}
        ],
        model="deepseek-chat"
    )
    print(response["choices"][0]["message"]["content"])
    ```
    '''

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(
        self, 
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 90,  # Aumentado para dar más tiempo a respuestas largas
        log_level: int = logging.INFO
    ):
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set in DEEPSEEK_API_KEY environment variable")

        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Configurar sesión con retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,  # Espera exponencial entre reintentos
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],  # Permitir retry en POST
            respect_retry_after_header=True,  # Respetar cabecera Retry-After
            raise_on_status=True,
            connect=3,  # Reintentos en problemas de conexión
            read=3,    # Reintentos en problemas de lectura
            status=3   # Reintentos en errores de status
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.timeout = timeout
        self.call_history: List[Dict] = []

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-reasoner",
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> Dict:
        '''
        Realiza una llamada al endpoint de chat completions.

        Args:
            messages (List[Dict[str, str]]): Lista de mensajes en formato
                [{"role": "system|user|assistant", "content": "mensaje"}, ...]
            model (str): Modelo a usar ('deepseek-chat' o 'deepseek-reasoner')
            temperature (float): Controla la creatividad (0.0 a 1.0)
            stream (bool): Si True, retorna respuesta en streaming
            **kwargs: Argumentos adicionales para la API

        Returns:
            Dict: Respuesta de la API procesada

        Raises:
            requests.exceptions.RequestException: Si hay un error en la llamada a la API
        '''
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en llamada a API: {str(e)}")
            raise

        # Registrar la llamada
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "messages": messages,
            "duration": time.time() - start_time,
            "status": response.status_code,
            "tokens_used": result.get("usage", {}).get("total_tokens", 0)
        }
        self.call_history.append(call_record)
        self.logger.info(f"Llamada exitosa a {model}: {call_record['tokens_used']} tokens usados")

        return result

    def get_call_history(self) -> List[Dict]:
        '''
        Retorna el historial de llamadas a la API.

        Returns:
            List[Dict]: Lista de registros de llamadas
        '''
        return self.call_history

    def generate_code(
        self,
        prompt: str,
        model: str = "deepseek-reasoner",
        **kwargs
    ) -> str:
        '''
        Genera código a partir de un prompt o descripción.

        Args:
            prompt (str): Descripción del código a generar
            model (str): Modelo a usar (default: deepseek-reasoner)
            **kwargs: Argumentos adicionales para chat

        Returns:
            str: Código generado

        Ejemplo:
            ```python
            client = DeepseekClient()
            prompt = """
            Escribe una función que:
            1. Recibe una lista de números
            2. Calcula la media y desviación estándar
            3. Retorna un diccionario con los resultados
            """
            code = client.generate_code(prompt)
            print(code)
            ```
        '''
        messages = [
            {
                "role": "system",
                "content": "You are a helpful programming assistant. Generate only Python code based on the given description. Include comments and error handling."
            },
            {
                "role": "user",
                "content": f"Generate Python code for the following task:\n\n{prompt}"
            }
        ]

        response = self.chat(
            messages=messages,
            model=model,
            temperature=0.2,  # Menor temperatura para código más determinista
            **kwargs
        )

        return response["choices"][0]["message"]["content"]

# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Crear cliente
    client = DeepseekClient()

    # Ejemplo simple con deepseek-chat
    response = client.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "¿Cuál es la capital de Francia?"}
        ],
        model="deepseek-chat"
    )
    print("Chat response:", response["choices"][0]["message"]["content"])

    # Ejemplo de generación de código
    code = client.generate_code("""
    Escribe una función que:
    1. Recibe una lista de números
    2. Calcula la media y desviación estándar
    3. Retorna un diccionario con los resultados
    """)
    print("\nGenerated code:\n", code)

    # Mostrar historial de llamadas
    print("\nCall history:")
    for call in client.get_call_history():
        print(f"- {call['timestamp']}: {call['model']} ({call['tokens_used']} tokens)")