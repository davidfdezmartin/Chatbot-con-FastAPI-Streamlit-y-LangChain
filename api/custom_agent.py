import os
import json
from langchain.agents import initialize_agent, Tool
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from elasticsearch import Elasticsearch, helpers
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# Definición de la ruta del archivo JSON
json_path = './data/clinica_mayo.json'

# Función para guardar datos en la ruta definida
def save_clinica_mayo_data(data):
    with open(json_path, 'w') as f:
        json.dump(data, f)

# Función para cargar datos desde la ruta definida
def load_clinica_mayo_data():
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            return json.load(f)
    return []

# Función para realizar web scraping en Mayo Clinic
def fetch_clinica_mayo_data(disease):
    url = f"https://www.mayoclinic.org/diseases-conditions/{disease}/symptoms-causes/syc-20355880"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        description_tag = soup.find('div', {'class': 'content'})
        if description_tag:
            description = description_tag.get_text().strip()
            data = load_clinica_mayo_data()
            data.append({
                "disease": disease,
                "source": "Mayo Clinic",
                "description": description
            })
            save_clinica_mayo_data(data)
            return description
    return "No se encontró información en Mayo Clinic."

# Función para crear el agente con herramientas personalizadas
def create_custom_tools_agent(model, tools, prompt):
    return initialize_agent(
        tools=tools,
        llm=model,
        agent_type="chat-conversational-react-description",
        prompt_template=prompt
    )

# Definir las herramientas personalizadas
def get_custom_tools():
    user_agent = 'MyApp/1.0 (example@example.com)'
    wikipedia_api_wrapper = WikipediaAPIWrapper(
        language='es', top_k_results=1, doc_content_chars_max=200, user_agent=user_agent)
    wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_api_wrapper)

    arxiv_api_wrapper = ArxivAPIWrapper(
        top_k_results=1, doc_content_chars_max=200)
    arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api_wrapper)

    clinica_mayo_tool = Tool(
        name="Mayo Clinic",
        func=lambda q: fetch_clinica_mayo_data(q.replace(" ", "-").lower()),
        description="Busca información sobre enfermedades en el sitio web de Mayo Clinic."
    )

    return [wikipedia_tool, arxiv_tool, clinica_mayo_tool]

# Función para procesar la consulta del usuario y devolver la respuesta adecuada
def process_query(query, lang='en'):
    tools = get_custom_tools()
    translator = Translator()

    # Traducir la pregunta al inglés si es necesario
    query_en = translator.translate(query, dest='en').text if lang == 'es' else query

    model = HuggingFaceHub(repo_id="LLaMA-3", model_kwargs={"temperature": 0.7}, huggingfacehub_api_token=os.getenv('HUGGING_FACE_API_TOKEN'))
    prompt_template = """
    Utiliza la siguiente información para responder la pregunta del usuario.
    Si no sabes la respuesta, simplemente di que no lo sabes, no inventes una respuesta.

    Contexto: {context}
    Pregunta: {input}

    Devuelve solo la respuesta útil a continuación y nada más.
    Respuesta útil:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    agent = create_custom_tools_agent(model, tools, prompt)

    # Ejecutar la consulta utilizando el agente
    response = agent.invoke({'input': query_en})

    # Traducir la respuesta de vuelta al español si es necesario
    response_es = translator.translate(response['output'], dest='es').text if lang == 'es' else response['output']

    return response_es

# Función para buscar datos en Elasticsearch
def search_data_in_es(index_name, query):
    es_url = f"https://{os.getenv('ELASTICSEARCH_USERNAME')}:{os.getenv('ELASTICSEARCH_PASSWORD')}@{os.getenv('ELASTICSEARCH_ENDPOINT')}:443"
    es = Elasticsearch(es_url)
    search_query = {
        "query": {
            "match": {
                "disease": query
            }
        }
    }
    response = es.search(index=index_name, body=search_query)
    return response['hits']['hits']
