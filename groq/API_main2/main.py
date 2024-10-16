import os
import time
from fastapi import FastAPI, Request
from googletrans import Translator
from functools import lru_cache
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.document_loaders import CSVLoader, JSONLoader, PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from api.custom_agent import create_custom_tools_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

cache = Cache.from_url("memory://", serializer=JsonSerializer())

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("No se ha configurado la clave API de GROQ en las variables de entorno.")

@lru_cache
def get_model():
    model_name = "ydshieh/tiny-random-gptj-para-responder-preguntas"
    return ChatGroq(model_name=model_name, groq_api_key=GROQ_API_KEY)

model = get_model()

prompt = ChatPromptTemplate.from_template(
    """
    Responda las preguntas según el contexto proporcionado.
    Proporcione la respuesta más precisa según la pregunta.
    <context>
    {context}
    </context>
    Preguntas: {input}
    """
)

@app.on_event("startup")
async def startup_event():
    embeddings = OllamaEmbeddings()
    docs = await load_documents()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    vectors = FAISS.from_documents(final_documents, embeddings)
    app.state.vectors = vectors
    wikipedia_api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
    app.state.wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_api_wrapper)
    arxiv_api_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
    app.state.arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)

@app.post("/ask")
async def ask_question(request: Request):
    start_time = time.time()
    
    data = await request.json()
    question = data.get("question")
    
    if not question:
        return {"error": "No se proporcionó pregunta."}
    
    translator = Translator()
    question_en = translator.translate(question, dest='en').text
    
    tools = [app.state.wikipedia_tool, app.state.arxiv_tool]
    agent = create_custom_tools_agent(model, tools, prompt)
    
    cached_response = await cache.get(question_en)
    if cached_response:
        response = cached_response
    else:
        response = agent.invoke({'input': question_en})
        await cache.set(question_en, response, ttl=3600)  # Cache the response for 1 hour
    
    response_es = translator.translate(response['output'], dest='es').text
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    return {"answer": response_es, "context": response["intermediate_steps"], "processing_time": processing_time}

@cache.cached(ttl=3600)  # Cache the function for 1 hour
async def load_documents():
    try:
        pdf_loader = PyPDFDirectoryLoader("./ruta/al/directorio/pdf")
        csv_loader = CSVLoader("./ruta/al/archivo.csv")
        json_loader = JSONLoader("./ruta/al/archivo.json")
        return pdf_loader.load() + csv_loader.load() + json_loader.load()
    except Exception as e:
        print(f"Error cargando documentos: {e}")
        return []
