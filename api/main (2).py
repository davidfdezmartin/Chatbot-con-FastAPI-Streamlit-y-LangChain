
import os
from fastapi import FastAPI, Request
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader, CSVLoader, JSONLoader
from dotenv import load_dotenv
from googletrans import Translator
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from custom_agent import create_custom_tools_agent
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = FastAPI()

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv('GROQ_API_KEY')

model_name = "ydshieh/tiny-random-gptj-for-question-answering"
model = ChatGroq(model_name=model_name, groq_api_key=groq_api_key)

prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the context provided.
    Provide the most accurate answer based on the question.
    <context>
    {context}
    </context>
    Questions: {input}
    """
)

def create_document_processing_pipeline():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    embeddings = OllamaEmbeddings()
    
    def load_and_split_documents():
        pdf_loader = PyPDFDirectoryLoader("./ruta/al/directorio/pdf")
        pdf_docs = pdf_loader.load()

        csv_loader = CSVLoader("./ruta/al/archivo.csv")
        csv_docs = csv_loader.load()

        json_loader = JSONLoader("./ruta/al/archivo.json")
        json_docs = json_loader.load()

        docs = pdf_docs + csv_docs + json_docs
        return text_splitter.split_documents(docs)
    
    docs = load_and_split_documents()
    vectors = FAISS.from_documents(docs, embeddings)
    
    return vectors

@app.on_event("startup")
async def startup_event():
    app.state.vectors = create_document_processing_pipeline()

    wikipedia_api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
    app.state.wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_api_wrapper)

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data["question"]

    translator = Translator()
    question_en = translator.translate(question, dest='en').text

    # Crear el agente utilizando el modelo GPT-J con Groq
    tools = [app.state.wikipedia_tool, MayoClinicQueryRun(), ClinVarQueryRun()]
    agent = create_custom_tools_agent(model, tools, prompt)
    
    response = agent.invoke({'input': question_en})

    response_es = translator.translate(response['output'], dest='es').text

    return {"respuesta": response_es, "contexto": response["intermediate_steps"]}

def MayoClinicQueryRun(disease):
    url = f"https://www.mayoclinic.org/diseases-conditions/{disease}/symptoms-causes/syc-20376178"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    symptoms = soup.find('div', {'class': 'content'}).get_text(separator="\n").strip()
    return symptoms

def ClinVarQueryRun(gene):
    url = f"https://www.ncbi.nlm.nih.gov/clinvar/?term={gene}[gene]"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    genetics = soup.find('div', {'class': 'docsum-content'}).get_text(separator="\n").strip()
    return genetics
