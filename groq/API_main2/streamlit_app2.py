import streamlit as st
import requests

st.title("Demostración de Chatgroq con Llama3")

prompt1 = st.text_input("Ingrese su pregunta sobre los documentos (en español)")

if st.button("Obtener respuesta"):
    response = requests.post("http://localhost:8000/ask", json={"question": prompt1})
    result = response.json()

    st.write("Respuesta:")
    st.write(result['respuesta'])

    with st.expander("Detalles adicionales"):
        st.write("Contexto:")
        for step in result["contexto"]:
            st.write(step)
