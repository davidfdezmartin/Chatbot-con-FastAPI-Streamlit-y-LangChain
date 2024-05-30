import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISGENET_EMAIL = os.getenv("DISGENET_EMAIL")
DISGENET_PASSWORD = os.getenv("DISGENET_PASSWORD")

api_host = "https://www.disgenet.org/api"
api_key = None
session = requests.Session()

def authenticate():
    global api_key
    auth_params = {"email": DISGENET_EMAIL, "password": DISGENET_PASSWORD}
    try:
        response = session.post(api_host + '/auth/', data=auth_params)
        if response.status_code == 200:
            json_response = response.json()
            api_key = json_response.get("token")
            session.headers.update({"Authorization": f"Bearer {api_key}"})
        else:
            print(response.status_code)
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(e)
        print("Error during the request.")

def get_disease_associated_genes(gene_id, source='UNIPROT'):
    if not api_key:
        authenticate()
    response = session.get(f"{api_host}/gda/gene/{gene_id}", params={'source': source})
    return response.json()

def get_gene_associated_diseases(disease_id, source='UNIPROT'):
    if not api_key:
        authenticate()
    response = session.get(f"{api_host}/gda/disease/{disease_id}", params={'source': source})
    return response.json()
