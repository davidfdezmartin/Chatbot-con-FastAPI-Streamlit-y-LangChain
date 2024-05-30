# se lanza desde el terminal con uvicorn api.main:app --reload
# y el servidor montado se vera en: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from googletrans import Translator
from langchain_community.llms import ChatGroq  # Cambiado a langchain_community
from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.tools import WikipediaQueryRun, ArxivQueryRun
from langchain.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from custom_agent import create_custom_tools_agent
from disgenet import get_disease_associated_genes, get_gene_associated_diseases

load_dotenv()

app = FastAPI()

# Configurar el caché correctamente
cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PDF_DIRECTORY_PATH = os.getenv("PDF_DIRECTORY_PATH")

if not GROQ_API_KEY:
    raise ValueError("No se ha configurado la clave API de GROQ en las variables de entorno.")
if not PDF_DIRECTORY_PATH:
    raise ValueError("No se ha configurado el directorio de PDFs en las variables de entorno.")

@lru_cache
def get_model():
    model_name = "ydshieh/tiny-random-gptj-para-responder-preguntas"
    return ChatGroq(model_name=model_name, groq_api_key=GROQ_API_KEY)

model = get_model()

prompt_template = """
Utiliza la siguiente información para responder la pregunta del usuario.
Si no sabes la respuesta, simplemente di que no lo sabes, no inventes una respuesta.

Contexto: {context}
Pregunta: {input}

Devuelve solo la respuesta útil a continuación y nada más.
Respuesta útil:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

@app.on_event("startup")
async def startup_event():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    docs = await load_documents()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs)
    vectors = FAISS.from_documents(final_documents, embeddings)
    app.state.vectors = vectors
    
    user_agent = 'MyApp/1.0 (example@example.com)'
    wikipedia_api_wrapper = WikipediaAPIWrapper(language='es', top_k_results=1, doc_content_chars_max=200, user_agent=user_agent)
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

@app.get("/disease_genes/{gene_id}")
async def disease_genes(gene_id: str):
    data = get_disease_associated_genes(gene_id)
    return data

@app.get("/gene_diseases/{disease_id}")
async def gene_diseases(disease_id: str):
    data = get_gene_associated_diseases(disease_id)
    return data

@cache.cached(ttl=3600)  # Cache the function for 1 hour
async def load_documents():
    try:
        pdf_loader = PyPDFDirectoryLoader(PDF_DIRECTORY_PATH)
        return pdf_loader.load()
    except Exception as e:
        print(f"Error cargando documentos: {e}")
        return []
