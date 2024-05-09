# Chatbot con FastAPI, Streamlit y LangChain

Este repositorio contiene un chatbot desarrollado utilizando FastAPI, Streamlit y LangChain, junto con el modelo de lenguaje GPT-J y el almacenamiento vectorial. El chatbot puede responder preguntas basadas en documentos proporcionados en formatos PDF, CSV y JSON, y utiliza herramientas adicionales como Wikipedia y Arxiv para proporcionar respuestas más completas.

## Requisitos previos
- Python 3.7 o superior
- Cuenta de Groq

## Pasos de configuración

1. **Clonar el repositorio:**
   - Abre una terminal o línea de comandos.
   - Navega hasta el directorio donde deseas clonar el repositorio.
   - Ejecuta el siguiente comando para clonar el repositorio:
     ```
     git clone https://github.com/tu-usuario/nombre-del-repositorio.git
     ```

2. **Crear y activar un entorno virtual (opcional pero recomendado):**
   - Navega hasta el directorio del repositorio clonado:
     ```
     cd nombre-del-repositorio
     ```
   - Crea un nuevo entorno virtual:
     ```
     python -m venv venv
     ```
   - Activa el entorno virtual:
     - En Windows:
       ```
       venv\Scripts\activate
       ```
     - En macOS y Linux:
       ```
       source venv/bin/activate
       ```

3. **Instalar las dependencias:**
   - Con el entorno virtual activado, ejecuta el siguiente comando para instalar las dependencias:
     ```
     pip install -r requirements.txt
     ```

4. **Configurar las variables de entorno:**
   - En el directorio raíz del repositorio, crea un nuevo archivo llamado `.env`.
   - Abre el archivo `.env` en un editor de texto.
   - Agrega la siguiente línea al archivo, reemplazando `TU_CLAVE_API_GROQ` con tu clave de API de Groq:
     ```
     GROQ_API_KEY=TU_CLAVE_API_GROQ
     ```
   - Guarda y cierra el archivo `.env`.

## Pasos para abrir y utilizar la API

1. **Ejecutar la aplicación FastAPI:**
   - En una terminal o línea de comandos, navega hasta el directorio del repositorio.
   - Asegúrate de tener el entorno virtual activado.
   - Ejecuta el siguiente comando para iniciar la aplicación FastAPI:
     ```
     uvicorn main:app --reload
     ```
   - La API estará disponible en `http://localhost:8000`.

2. **Ejecutar la aplicación Streamlit:**
   - Abre otra terminal o línea de comandos.
   - Navega hasta el directorio del repositorio.
   - Asegúrate de tener el entorno virtual activado.
   - Ejecuta el siguiente comando para iniciar la aplicación Streamlit:
     ```
     streamlit run streamlit_app.py
     ```
   - Se abrirá una ventana del navegador con la interfaz de usuario de Streamlit.

3. **Interactuar con el chatbot:**
   - En la interfaz de usuario de Streamlit, ingresa tu pregunta en el campo de texto provisto.
   - Haz clic en el botón "Obtener respuesta" para enviar la pregunta al chatbot.
   - El chatbot procesará la pregunta y mostrará la respuesta generada junto con el contexto relevante.
   - Puedes expandir la sección "Detalles adicionales" para ver el contexto y los pasos intermedios utilizados por el chatbot para generar la respuesta.

¡Eso es todo! Ahora puedes utilizar el chatbot y explorar sus capacidades de respuesta basadas en los documentos proporcionados y las herramientas adicionales integradas.

Si tienes alguna pregunta o encuentras algún problema, no dudes en abrir un issue en este repositorio.

¡Disfruta usando el chatbot!
