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

# prueba de pedirle por esquizofrenia
import requests

# Set API endpoint and disease ID
api_endpoint = "https://www.disgenet.org/api"
disease_id = "C0025218"  # Schizophrenia

# Set API key (replace with your own API key)
api_key = "YOUR_API_KEY_HERE"

# Set headers with API key
headers = {"Authorization": f"Bearer {api_key}"}

# Define parameters for the API request
params = {
    "disease": disease_id,
    "source": "UNIPROT",  # Optional parameter
    "format": "json"  # Optional parameter
}

# Send GET request to DisGeNET API
response = requests.get(f"{api_endpoint}/gda/genes/disease/{disease_id}", headers=headers, params=params)

# Check if the response was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()

    # Print genes associated with Schizophrenia
    print("Genes associated with Schizophrenia:")
    for gene in data["genes"]:
        print(f"Gene ID: {gene['geneId']}, Gene Symbol: {gene['geneSymbol']}")

    # Print additional information and graphs (if available)
    for gene in data["genes"]:
        print(f"Gene ID: {gene['geneId']}, Gene Symbol: {gene['geneSymbol']}")
        print("  Associated Diseases:")
        for disease in gene["associatedDiseases"]:
            print(f"    {disease['diseaseId']}: {disease['diseaseName']}")
        print("  Gene-Disease Associations:")
        for association in gene["geneDiseaseAssociations"]:
            print(f"    {association['diseaseId']}: {association['diseaseName']}")
        print("  Graphs:")
        for graph in gene["graphs"]:
            print(f"    {graph['graphId']}: {graph['graphName']}")

else:
    print("Error:", response.status_code)
