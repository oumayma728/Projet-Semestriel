import requests
import json
from typing import List, Dict, Any
class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def test_connection(self) -> bool:
        """check if ollama is reachable"""
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except requests.RequestException:
            return False
    def get_models(self) ->List[str]:
        """get list of available models from ollama"""
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                models = response.json()
                return [model["name"] for model in models]
            response = requests.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                models = response.json()
                return [model["name"] for model in models]
            else:
                return []
        except requests.RequestException:
            return []
        