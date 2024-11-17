import json
from typing import  Dict
from FileHandler import FileHandler
class JsonHandler(FileHandler):
    """JSON file handler"""
    def read_file(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def write_file(self, data: Dict) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
