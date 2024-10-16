### Integración de Archivos desde GitHub y Limpieza de Contenido en Python

#### Objetivo
El objetivo de este trabajo es demostrar cómo cargar documentos desde un repositorio de GitHub, procesarlos y limpiarlos utilizando Python, asegurando que el código sea portable y fácil de usar por otros colaboradores.

#### Pasos Realizados

1. **Clonación del Repositorio**
   Clonamos el repositorio desde GitHub usando GitHub Desktop para tener una copia local de los archivos.

2. **Configuración de Variables de Entorno**
   Utilizamos un archivo `.env` para gestionar las variables de entorno, facilitando el acceso a URLs y tokens de API de manera segura y flexible.

   **Contenido del archivo `.env`**:
   ```plaintext
   ROOT=https://raw.githubusercontent.com/davidfdezmartin/Chatbot-con-FastAPI-Streamlit-y-LangChain/main
   HUGGING_FACE_API_TOKEN=tu_token_de_hugging_face
   ```

3. **Carga del Archivo desde GitHub**
   Utilizamos la biblioteca `requests` para descargar el contenido del archivo directamente desde GitHub utilizando la URL cruda.

4. **Guardado Temporal y Carga del Archivo**
   El contenido descargado se guarda en un archivo temporal que luego se carga utilizando `TextLoader` de la biblioteca `langchain_community`.

5. **Limpieza del Contenido del Documento**
   Implementamos una función para limpiar el contenido del documento, eliminando caracteres especiales y etiquetas HTML innecesarias.

#### Código Completo

```python
import requests
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Usar root como base del GitHub
root = os.getenv("ROOT")
if not root:
    raise ValueError("ROOT no encontrado en el archivo .env")

print("Root de GitHub:", root)

# URL del archivo en GitHub
file_path = f"{root}/documentos_y_matcomplement/docuentreno/md/Cholesterol-Myths-vs-Facts-Spanish.md"
print("URL del archivo:", file_path)

# Descargar el contenido del archivo
response = requests.get(file_path)
if response.status_code != 200:
    raise RuntimeError(f"Error al descargar el archivo desde {file_path}")

# Guardar el contenido en un archivo temporal
with open("temp.md", "w", encoding="utf-8") as temp_file:
    temp_file.write(response.text)

# Cargar el documento .md desde el archivo temporal
text_loader = TextLoader("temp.md")
documents = text_loader.load()

# Limpiar el contenido del documento
def clean_text(text):
    # Eliminar caracteres especiales no deseados
    text = text.replace('\ufeff', '')
    text = text.replace('<a name="br1"></a>', '')
    return text.strip()

# Procesar y limpiar el contenido del documento
cleaned_documents = []
for doc in documents:
    cleaned_text = clean_text(doc.page_content)
    cleaned_documents.append(cleaned_text)

# Mostrar el contenido limpio del documento
for doc in cleaned_documents:
    print("Contenido limpio del documento:", doc)
```

#### Explicación del Código

1. **Carga de Variables de Entorno**:
   Se utiliza la biblioteca `dotenv` para cargar las variables de entorno desde el archivo `.env`, permitiendo una configuración flexible y segura.
   
   ```python
   load_dotenv()
   root = os.getenv("ROOT")
   if not root:
       raise ValueError("ROOT no encontrado en el archivo .env")
   ```

2. **Construcción de la URL del Archivo**:
   La URL del archivo se construye utilizando la variable `root` obtenida del archivo `.env`.
   
   ```python
   file_path = f"{root}/documentos_y_matcomplement/docuentreno/md/Cholesterol-Myths-vs-Facts-Spanish.md"
   ```

3. **Descarga del Archivo**:
   Utilizamos `requests.get` para descargar el contenido del archivo desde la URL construida.
   
   ```python
   response = requests.get(file_path)
   if response.status_code != 200:
       raise RuntimeError(f"Error al descargar el archivo desde {file_path}")
   ```

4. **Guardado Temporal del Archivo**:
   El contenido descargado se guarda en un archivo temporal llamado `temp.md`.
   
   ```python
   with open("temp.md", "w", encoding="utf-8") as temp_file:
       temp_file.write(response.text)
   ```

5. **Carga y Procesamiento del Documento**:
   Se utiliza `TextLoader` para cargar el contenido del archivo temporal y luego se procesa para eliminar caracteres especiales y etiquetas HTML innecesarias.
   
   ```python
   text_loader = TextLoader("temp.md")
   documents = text_loader.load()
   
   def clean_text(text):
       text = text.replace('\ufeff', '')
       text = text.replace('<a name="br1"></a>', '')
       return text.strip()
   
   cleaned_documents = []
   for doc in documents:
       cleaned_text = clean_text(doc.page_content)
       cleaned_documents.append(cleaned_text)
   ```

6. **Impresión del Contenido Limpio**:
   Se imprime el contenido limpio del documento para verificar el resultado.
   
   ```python
   for doc in cleaned_documents:
       print("Contenido limpio del documento:", doc)
   ```

### Conclusión
Este enfoque permite cargar y procesar documentos desde un repositorio de GitHub de manera eficiente, asegurando que el contenido sea limpio y fácil de manejar. La utilización de variables de entorno y la descarga dinámica del contenido aseguran que el código sea portable y fácil de mantener, lo que facilita la colaboración en proyectos de datos y procesamiento de texto.

