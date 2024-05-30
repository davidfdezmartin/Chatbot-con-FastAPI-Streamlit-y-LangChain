import requests
from langchain.tools import Tool

class DisGeNETAPIWrapper:
    def __init__(self, email, password, base_url="https://www.disgenet.org/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.api_key = self.authenticate(email, password)
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    
    def authenticate(self, email, password):
        auth_params = {"email": email, "password": password}
        try:
            response = self.session.post(f"{self.base_url}/auth/", data=auth_params)
            if response.status_code == 200:
                json_response = response.json()
                return json_response.get("token")
            else:
                print(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
        return None
    
    def query_gene(self, gene_id, source='UNIPROT'):
        try:
            response = self.session.get(f"{self.base_url}/gda/gene/{gene_id}", params={'source': source})
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request Exception: {e}"}


class DisGeNETQueryRun(Tool):
    def __init__(self, api_wrapper):
        self.api_wrapper = api_wrapper

    def run(self, input_text):
        # Assuming the input is a gene ID
        result = self.api_wrapper.query_gene(input_text)
        return result