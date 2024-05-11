
# Chatbot con FastAPI, Streamlit y LangChain

Este repositorio contiene un chatbot desarrollado utilizando FastAPI, Streamlit y LangChain, junto con los modelos de lenguaje Ollama 3 y un LLM genérico. El chatbot puede responder preguntas basadas en documentos proporcionados en formatos PDF, CSV y JSON, y utiliza herramientas adicionales como Wikipedia y Arxiv para proporcionar respuestas más completas.

![Arquitectura del Chatbot](readme.webp)

## Requisitos previos
- Python 3.7 o superior
- Redis (opcional, para configuraciones avanzadas de caché)

## Instalación

Clonar el repositorio y navegar al directorio del proyecto:
```
git clone https://github.com/tu-usuario/nombre-del-repositorio.git
cd nombre-del-repositorio
```

Instalar las dependencias:
```
pip install -r requirements.txt
```

## Configuración

### Configurar las variables de entorno
Crear un archivo `.env` en el directorio raíz y añadir la clave API:
```
GROQ_API_KEY=TU_CLAVE_API_GROQ
```

### Caché
El sistema utiliza `aiocache` para caché en memoria, mejorando la eficiencia y la velocidad de respuesta del sistema. La configuración por defecto es suficiente para la mayoría de los casos, pero se puede configurar para usar Redis si se requiere persistencia y rendimiento mejorado.

## Configuración Avanzada de Caché con Redis

La aplicación está preparada para utilizar Redis como un sistema de caché para mejorar el rendimiento al almacenar respuestas frecuentes y reducir la carga en los servidores. Para habilitar esta funcionalidad, sigue estos pasos:

### Instalación de Redis

1. **Instalar Redis en tu sistema local o servidor:**
   - Puedes descargar Redis desde [la página oficial](https://redis.io/download) o utilizar un servicio gestionado de Redis proporcionado por servicios de hosting como Heroku, Amazon Web Services, o Google Cloud Platform.

2. **Configuración de Redis:**
   - Asegúrate de que Redis está corriendo en tu sistema y toma nota del puerto y la dirección IP (usualmente `localhost` en el puerto `6379`).

### Configurar Redis en la Aplicación

Para utilizar Redis como backend de caché:

1. **Descomenta las líneas en `streamlit_app.py` relacionadas con `aioredis` y `aiocache`.**
   - Estas líneas conectan la aplicación con tu instancia de Redis y configuran `aiocache` para usar Redis como almacenamiento de caché.

2. **Ajusta las variables de conexión a Redis si es necesario.**
   - Si estás utilizando una configuración no estándar o un servicio gestionado de Redis, ajusta las variables de conexión en el código para reflejar tu configuración específica.

### Dependencias

Asegúrate de que `aioredis` y `aiocache` están instalados. Si no están presentes en tu entorno, instálalos usando:

```
pip install aioredis aiocache
```

## Uso de la API

Ejecutar la aplicación FastAPI:
```
uvicorn main:app --reload
```
La API estará disponible en `http://localhost:8000`.

Ejecutar la interfaz de usuario de Streamlit:
```
streamlit run streamlit_app.py
```

## Diagrama de Flujo del Proceso
```mermaid
graph TD
    A[Inicio: Usuario accede a la aplicación Streamlit] --> B[Usuario ingresa pregunta en español]
    B --> C[Pregunta enviada a la API FastAPI]
    C --> D[Traducción de la pregunta al inglés usando Google Translate]
    D --> E[Agente personalizado recibe la pregunta traducida]
    E --> F{Tipo de pregunta}
    F --> |Pregunta general| G[Búsqueda en Wikipedia]
    F --> |Pregunta médica específica| H[Búsqueda en documentos médicos]
    F --> |Pregunta sobre estudios científicos| I[Búsqueda en Arxiv]
    G --> J[Compilación de resultados de Wikipedia]
    H --> K[Compilación de resultados de documentos médicos]
    I --> L[Compilación de resultados de Arxiv]
    J --> M[Generación de respuesta en inglés utilizando el modelo Ollama 3 LLM]
    K --> M
    L --> M
    M --> N[Traducción de la respuesta al español usando Google Translate]
    N --> O[Respuesta traducida al español devuelta a la interfaz de usuario de Streamlit]
    O --> P[Respuesta en español mostrada al usuario]
    P --> Q[Expansión: Detalles adicionales y contexto utilizado]
```

## Contacto y Soporte
Si tienes alguna pregunta o encuentras algún problema, no dudes en abrir un issue en este repositorio.

¡Disfruta usando el chatbot!
