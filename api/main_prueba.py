# se ejecuta no con play solo, sino luego uvicorn api.main_prueba:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI
from dotenv import load_dotenv
from aiocache import Cache
from aiocache.serializers import JsonSerializer

load_dotenv()

app = FastAPI()

# Configurar el caché sin el argumento 'serializer'
cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

@app.get("/")
async def read_root():
    return {"Hello": "World"}
