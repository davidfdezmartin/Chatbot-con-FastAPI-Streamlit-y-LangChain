import os
import time
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from googletrans import Translator
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from custom_agent import create_custom_tools_agent, process_query
from disgenet import get_disease_associated_genes, get_gene_associated_diseases
from functools import lru_cache
import json
import requests
from elasticsearch import Elasticsearch, helpers

load_dotenv()

app = FastAPI()

# Configurar el caché correctamente
cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PDF_DIRECTORY_PATH = os.getenv("PDF_DIRECTORY_PATH")
HUGGING_FACE_API_TOKEN = os.getenv('HUGGING_FACE_API_TOKEN')
ELASTICSEARCH_ENDPOINT = os.getenv('ELASTICSEARCH_ENDPOINT')
ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')

if not GROQ_API_KEY:
    raise ValueError(
        "No se ha configurado la clave API de GROQ en las variables de entorno.")
if not PDF_DIRECTORY_PATH:
    raise ValueError(
        "No se ha configurado el directorio de PDFs en las variables de entorno.")
if not HUGGING_FACE_API_TOKEN:
    raise ValueError(
        "No se ha configurado el token API de Hugging Face en las variables de entorno.")
if not ELASTICSEARCH_ENDPOINT:
    raise ValueError(
        "No se ha configurado el endpoint de Elasticsearch en las variables de entorno.")
if not ELASTICSEARCH_USERNAME:
    raise ValueError(
        "No se ha configurado el nombre de usuario de Elasticsearch en las variables de entorno.")
if not ELASTICSEARCH_PASSWORD:
    raise ValueError(
        "No se ha configurado la contraseña de Elasticsearch en las variables de entorno.")

# Configuración de Elasticsearch con credenciales
es_url = f"https://{ELASTICSEARCH_USERNAME}:{ELASTICSEARCH_PASSWORD}@{ELASTICSEARCH_ENDPOINT}:443"
es = Elasticsearch(es_url)

# Verificar la conexión a Elasticsearch
try:
    es.ping()
    print("Conexión exitosa a Elasticsearch")
except Exception as e:
    print(f"No se pudo establecer conexión: {e}")

# Crear índice en Elasticsearch
index_name = "genetic_information"
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

# Función para cargar y dividir documentos PDF
def load_and_split_pdf(pdf_path):
    pdf_loader = PyPDFDirectoryLoader(pdf_path)
    docs = pdf_loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    return final_documents

# Función para vectorizar documentos y almacenarlos
def vectorize_and_store(documents):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectors = FAISS.from_documents(documents, embeddings)
    return vectors

@lru_cache
def load_documents_and_vectors():
    pdf_path = PDF_DIRECTORY_PATH
    documents = load_and_split_pdf(pdf_path)
    vectors = vectorize_and_store(documents)
    return vectors

@lru_cache
def get_general_model():
    return HuggingFaceHub(repo_id="LLaMA-3", model_kwargs={"temperature": 0.7}, huggingfacehub_api_token=HUGGING_FACE_API_TOKEN)

@lru_cache
def get_medical_model():
    return HuggingFaceHub(repo_id="Med-PaLM-2", model_kwargs={"temperature": 0.7}, huggingfacehub_api_token=HUGGING_FACE_API_TOKEN)

general_model = get_general_model()
medical_model = get_medical_model()

prompt_template = """
Utiliza la siguiente información para responder la pregunta del usuario.
Si no sabes la respuesta, simplemente di que no lo sabes, no inventes una respuesta.

Contexto: {context}
Pregunta: {input}

Devuelve solo la respuesta útil a continuación y nada más.
Respuesta útil:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

def classify_question(question):
    basic_keywords = ["qué es", "síntomas", "tratamiento"]
    intermediate_keywords = ["prevención", "diagnóstico", "medicación"]
    advanced_keywords = ["gen", "mutación", "riesgo genético"]

    if any(keyword in question.lower() for keyword in basic_keywords):
        return "basico"
    elif any(keyword in question.lower() for keyword in intermediate_keywords):
        return "intermedio"
    elif any(keyword in question.lower() for keyword in advanced_keywords):
        return "avanzado"
    else:
        return "unknown"

def extract_disease_from_question(question):
    diseases = ["diabetes", "cáncer", "hipertensión", "fibrosis quística", "artritis", "asma", "alzheimer", "parkinson"]
    for disease in diseases:
        if disease.lower() in question.lower():
            return disease
    return "unknown"

def fetch_clinvar_data(disease):
    esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={disease}[disease/phenotype]+risk&retmode=json"
    esearch_response = requests.get(esearch_url)
    if esearch_response.status_code == 200:
        esearch_result = esearch_response.json()
        ids = esearch_result["esearchresult"]["idlist"]
        
        if ids:
            esummary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={','.join(ids)}&retmode=json"
            esummary_response = requests.get(esummary_url)
            if esummary_response.status_code == 200:
                return esummary_response.json()
    return None

def process_clinvar_data(data):
    records = []
    if data:
        for uid in data['result']['uids']:
            record = data['result'][uid]
            gene_info = 'N/A'
            if "genes" in record:
                genes = record["genes"]
                if genes:
                    gene_info = genes[0].get('symbol', 'N/A')
            
            mutation_info = 'N/A'
            if "variation_set" in record:
                variations = record["variation_set"]
                if variations:
                    mutation_info = variations[0].get('variation_name', 'N/A')
            
            description = record.get("description", "No description available.")
            if description == "N/A":
                description = record.get("summary", "No additional information provided.")
            
            record_data = {
                "gene": gene_info,
                "mutation": mutation_info,
                "description": description
            }
            
            records.append(record_data)
    return records

def fetch_and_process_clinvar_data(disease):
    raw_data = fetch_clinvar_data(disease)
    return process_clinvar_data(raw_data)

@app.on_event("startup")
async def startup_event():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectors = load_documents_and_vectors()
    app.state.vectors = vectors

@app.post("/ask")
async def ask_question(request: Request):
    start_time = time.time()

    data = await request.json()
    question = data.get("question")

    if not question:
        return {"error": "No se proporcionó pregunta."}

    translator = Translator()
    question_en = translator.translate(question, dest='en').text

    # Clasificar la pregunta
    question_type = classify_question(question_en)

    if question_type == "avanzado":
        # Buscar información técnica en Elasticsearch y ClinVar
        disease = extract_disease_from_question(question_en)
        es_results = process_query(disease, "es") # Llamada a la búsqueda en Elasticsearch
        clinvar_results = fetch_and_process_clinvar_data(disease)
        
        # Preparar contexto para el modelo
        context = "\n".join([
            f"Disease: {result['_source']['disease']}, Gene: {result['_source']['gene']}, Mutation: {result['_source']['mutation']}, Description: {result['_source']['description']}"
            for result in es_results
        ])
        
        if clinvar_results:
            context += "\n" + "\n".join([
                f"Gene: {record['gene']}, Mutation: {record['mutation']}, Description: {record['description']}"
                for record in clinvar_results
            ])
        
        model = medical_model
    elif question_type == "intermedio":
        # Usar información de la Clínica Mayo y la guía médica en PDF
        disease = extract_disease_from_question(question_en)
        context = f"Información sobre {disease} de fuentes confiables."
        model = medical_model
    elif question_type == "basico":
        # Usar Wikipedia y Arxiv para información general
        tools = app.state.tools
        context = "Información general sobre salud."
        model = general_model
        agent = create_custom_tools_agent(model, tools, prompt)
        
        cached_response = await cache.get(question_en)
        if cached_response:
            response = cached_response
        else:
            response = agent.invoke({'input': question_en})
            await cache.set(question_en, response, ttl=3600)
        
        response_es = translator.translate(response['output'], dest='es').text

        end_time = time.time()
        processing_time = end_time - start_time

        return {"answer": response_es, "context": response["intermediate_steps"], "processing_time": processing_time}
    else:
        # Si no se puede clasificar la pregunta, usar el modelo general para intentar responder
        model = general_model
        input_data = {
            "input": question_en,
            "context": "No se pudo clasificar la pregunta. Intenta proporcionar una respuesta general."
        }
        response = model.invoke(input_data)

        response_es = translator.translate(response['output'], dest='es').text

        if "no lo sé" in response_es.lower() or "no entiendo" in response_es.lower():
            response_es = "Lo siento, no entiendo la pregunta. Por favor, intente formularla de otra manera."

        end_time = time.time()
        processing_time = end_time - start_time

        return {"answer": response_es, "context": input_data["context"], "processing_time": processing_time}

    # Generar la respuesta usando el modelo seleccionado
    input_data = {
        "input": question_en,
        "context": context
    }
    response = model.invoke(input_data)

    response_es = translator.translate(response['output'], dest='es').text

    end_time = time.time()
    processing_time = end_time - start_time

    return {"answer": response_es, "context": context, "processing_time": processing_time}

@app.get("/disease_genes/{gene_id}")
async def disease_genes(gene_id: str):
    data = get_disease_associated_genes(gene_id)
    return data

@app.get("/gene_diseases/{disease_id}")
async def gene_diseases(disease_id: str):
    data = get_gene_associated_diseases(disease_id)
    return data

@cache.cached(ttl=3600)
async def load_documents():
    try:
        pdf_loader = PyPDFDirectoryLoader(PDF_DIRECTORY_PATH)
        return pdf_loader.load()
    except Exception as e:
        print(f"Error cargando documentos: {e}")
        return []
