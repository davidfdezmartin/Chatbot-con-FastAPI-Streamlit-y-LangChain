import streamlit as st
import requests
from aiocache import Cache
from aiocache.serializers import JsonSerializer

# Configuración inicial de aiocache para usar Redis
# (Descomentar las siguientes líneas cuando esté listo para usar Redis)
# import aioredis
#
# async def get_cache():
#     redis = await aioredis.create_redis_pool("redis://localhost:6379")
#     cache = Cache(Cache.REDIS, endpoint="localhost", port=6379, namespace="main", redis=redis, serializer=JsonSerializer())
#     return cache
#
# cache = get_cache()

st.title("Demostración de Chatgroq con Llama3")

prompt1 = st.text_input("Ingrese su pregunta sobre los documentos (en español)")

if st.button("Obtener respuesta"):
    # Intenta recuperar la respuesta desde la caché
    # (Descomenta las siguientes líneas cuando estés listo para usar Redis)
    # cached_response = await cache.get(prompt1)
    # if cached_response:
    #     response_data = cached_response
    # else:
    #     with st.spinner("Procesando la pregunta..."):
    #         response = requests.post("http://localhost:8000/ask", json={"question": prompt1})
    #         response_data = response.json()
    #     await cache.set(prompt1, response_data, ttl=60*60) # Cachea por 1 hora

    # Sin Redis, sólo llamando directamente al API
    with st.spinner("Procesando la pregunta..."):
        response = requests.post("http://localhost:8000/ask", json={"question": prompt1})
        response_data = response.json()

    st.write("Respuesta:")
    with st.spinner("Generando la respuesta..."):
        st.write(response_data['respuesta'])

    st.write(f"Tiempo de procesamiento: {response_data['tiempo_procesamiento']:.2f} segundos")

    with st.expander("Detalles adicionales"):
        st.write("Contexto:")
        for step in response_data["contexto"]:
            st.write(step)

    st.success("¡Respuesta generada con éxito!")
    st.balloons()
