import os
from dotenv import load_dotenv
import requests

load_dotenv()  # Load environment variables from .env file
DISGENET_API_KEY = os.getenv("DISGENET_API_KEY")
import os
from dotenv import load_dotenv
import requests

load_dotenv()  # Load environment variables from .env file
DISGENET_API_KEY = os.getenv("DISGENET_API_KEY")
DISGENET_API_KEY = "76360be811d4ee08ddb1369c58fa0f14d347704b"

api_host = "https://www.disgenet.org/api"
api_key = DISGENET_API_KEY
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {api_key}"})

def get_genes_associated_with_disease(disease_id, source='UNIPROT'):
    response = session.get(f"{api_host}/gda/disease/{disease_id}", params={'source': source})
    response.raise_for_status()
    return response.json()

# Example usage:
disease_id = "C0003856"
genes_associated_with_disease = get_genes_associated_with_disease(disease_id)
print(genes_associated_with_disease)

api_host = "https://www.disgenet.org/api"
api_key = DISGENET_API_KEY
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {api_key}"})

def get_genes_associated_with_disease(disease_id, source='UNIPROT'):
    response = session.get(f"{api_host}/gda/disease/{disease_id}", params={'source': source})
    response.raise_for_status()
    return response.json()

# Example usage:
disease_id = "C0003856"
genes_associated_with_disease = get_genes_associated_with_disease(disease_id)
print(genes_associated_with_disease)
