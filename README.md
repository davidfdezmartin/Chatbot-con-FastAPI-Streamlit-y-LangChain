
# Chatbot con FastAPI, Streamlit y LangChain

Este repositorio contiene un chatbot desarrollado utilizando FastAPI, Streamlit y LangChain, junto con los modelos de lenguaje Ollama 3 y un LLM genérico. El chatbot puede responder preguntas basadas en documentos proporcionados en formatos PDF, CSV y JSON, y utiliza herramientas adicionales como Wikipedia y Arxiv para proporcionar respuestas más completas.

![Arquitectura del Chatbot](readme.webp)

## Requisitos previos
- Python 3.7 o superior
- Cuenta de Groq (si aplicable)

## Configuración

### Clonar el repositorio
```
git clone https://github.com/davidfdezmartin/Chatbot-con-FastAPI-Streamlit-y-LangChain.git
cd Chatbot-con-FastAPI-Streamlit-y-LangChain
```

### Crear y activar un entorno virtual
En Windows:
```
python -m venv venv
venv\Scripts\activate
```
En macOS y Linux:
```
python -m venv venv
source venv/bin/activate
```

### Instalar las dependencias
```
pip install -r requirements.txt
```

### Configurar las variables de entorno
Crear un archivo `.env` en el directorio raíz y añadir la clave API:
```
GROQ_API_KEY=TU_CLAVE_API_GROQ
```

## Uso de la API

### Ejecutar la aplicación FastAPI
```
uvicorn main:app --reload
```
La API estará disponible en `http://localhost:8000`.

### Ejecutar la aplicación Streamlit
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
