import os
from fastapi import FastAPI, Request
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
from googletrans import Translator

load_dotenv()

app = FastAPI()

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(groq_api_key=groq_api_key,
               model_name="Llama3-8b-8192")

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

@app.on_event("startup")
async def startup_event():
    # ... (El código de inicio permanece igual)

@app.post("/ask")
async def ask_question(request: Request):
    prompt1 = await request.json()
    prompt1 = prompt1["question"]

    translator = Translator()
    prompt1_en = translator.translate(prompt1, dest='en').text

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = app.state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({'input': prompt1_en})

    response_es = translator.translate(response['respuesta'], dest='es').text

    return {"respuesta": response_es, "contexto": response["contexto"]}
