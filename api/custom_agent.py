import os
from bs4 import BeautifulSoup
import requests
import json

# Función para obtener datos de la Clínica Mayo
def scrape_mayo_clinic(disease_name):
    url = f"https://www.mayoclinic.org/diseases-conditions/{disease_name.replace(' ', '-').lower()}/symptoms-causes/syc-20355852"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        description_tag = soup.find('div', class_='content')
        description = description_tag.text.strip() if description_tag else "No description available."
        
        gene_tags = soup.find_all('a', href=True)
        genes = [tag.text.strip() for tag in gene_tags if '/tests-procedures' in tag['href']]
        
        return {
            "disease": disease_name,
            "description": description,
            "genes": genes
        }
    else:
        return {
            "disease": disease_name,
            "description": "No description available.",
            "genes": []
        }

# Función para cargar datos a Elasticsearch
def load_data_to_es(data, index_name, es):
    actions = [
        {
            "_index": index_name,
            "_source": item
        }
        for item in data
    ]
    helpers.bulk(es, actions)

# Guardar datos en un archivo JSON
def save_to_json(data, json_path):
    with open(json_path, 'w') as file:
        json.dump(data, file)

# Cargar datos desde un archivo JSON
def load_from_json(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)

# Definir la ruta del archivo JSON
json_path = './data/clinica_mayo.json'

# Obtener datos de la Clínica Mayo y guardarlos en el archivo JSON
disease_name = "Cystic Fibrosis"
mayo_data = scrape_mayo_clinic(disease_name)
save_to_json([mayo_data], json_path)
