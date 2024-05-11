
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
