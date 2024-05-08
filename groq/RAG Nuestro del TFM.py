import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.document_loaders import CSVLoader, JSONLoader
from dotenv import load_dotenv


load_dotenv()


os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv('GROQ_API_KEY')


st.title("Demostración de Chatgroq con Llama3")


llm = ChatGroq(groq_api_key=groq_api_key, 
               model_name="Llama3-8b-8192")


prompt = ChatPromptTemplate.from_template(
    """
    Responda las preguntas basándose en el contexto proporcionado. 
    Proporcione la respuesta más precisa según la pregunta.
    <contexto>
    {context}
    </contexto>
    Preguntas: {input}
    """
)


def vector_embedding():
    if "vectores" not in st.session_state:
        st.session_state.embeddings = OllamaEmbeddings()
        
        # Cargar documentos PDF
        pdf_loader = PyPDFDirectoryLoader("./ruta/al/directorio/pdf")
        pdf_docs = pdf_loader.load()
        
        # Cargar datos CSV
        csv_loader = CSVLoader("./ruta/al/archivo.csv")
        csv_docs = csv_loader.load()
        
        # Cargar datos JSON
        json_loader = JSONLoader("./ruta/al/archivo.json")
        json_docs = json_loader.load()
        
        # Combinar documentos de diferentes fuentes
        st.session_state.docs = pdf_docs + csv_docs + json_docs
        
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)


prompt1 = st.text_input("Ingrese su pregunta sobre los documentos")


if st.button("Incrustar documentos"):
    vector_embedding()
    st.write("La base de datos del almacén de vectores está lista")


import time


if prompt1:
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    start = time.process_time()
    response = retrieval_chain.invoke({'input': prompt1})
    print("Tiempo de respuesta:", time.process_time() - start)
    
    st.write(response['respuesta'])
    
    # Con un expansor de Streamlit
    with st.expander("Búsqueda de documentos similares"):
        # Encontrar los fragmentos relevantes
        for i, doc in enumerate(response["contexto"]):
            st.write(doc.page_content)
            st.write("---")