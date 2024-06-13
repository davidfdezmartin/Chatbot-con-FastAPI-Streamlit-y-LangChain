import streamlit as st
import requests
import aioredis
import asyncio
from aiocache import Cache
from aiocache.serializers import JsonSerializer

# Configuración inicial de aiocache para usar Redis
async def get_cache():
    redis = await aioredis.create_redis_pool("redis://localhost:6379")
    cache = Cache(Cache.REDIS, endpoint="localhost", port=6379, namespace="main", redis=redis, serializer=JsonSerializer())
    return cache

async def get_response_from_cache(prompt):
    cache = await get_cache()
    return await cache.get(prompt)

async def set_response_to_cache(prompt, response_data):
    cache = await get_cache()
    await cache.set(prompt, response_data, ttl=60*60)  # Cachear por 1 hora

async def fetch_response(prompt):
    with st.spinner("Procesando la pregunta..."):
        response = requests.post("http://localhost:8000/ask", json={"question": prompt})
        response_data = response.json()
    await set_response_to_cache(prompt, response_data)
    return response_data

# Título de la aplicación
st.title("Health and Wellness Assistant")

st.write("""
    Bienvenido al Asistente de Salud y Bienestar.
    Este bot está diseñado para responder preguntas sobre salud y bienestar,
    utilizando múltiples fuentes de información incluyendo web scraping,
    documentos PDF, búsquedas en Elasticsearch y más.
    Puede ayudarte a entender mejor condiciones médicas, encontrar información
    sobre tratamientos y síntomas, y proporcionarte datos genéticos relacionados
    con diversas enfermedades.
""")

# Entrada de texto para la pregunta del usuario
question = st.text_input("¿Tienes alguna pregunta sobre salud o genética?")

# Botón para obtener la respuesta
if st.button("Obtener respuesta"):
    response_data = asyncio.run(get_response_from_cache(question))
    if not response_data:
        response_data = asyncio.run(fetch_response(question))
    
    st.write("Respuesta:")
    with st.spinner("Generando la respuesta..."):
        st.write(response_data['answer'])

    st.write(f"Tiempo de procesamiento: {response_data['processing_time']:.2f} segundos")

    with st.expander("Detalles adicionales"):
        st.write("Contexto:")
        for step in response_data["context"]:
            st.write(step)

    st.success("¡Respuesta generada con éxito!")
    st.balloons()
