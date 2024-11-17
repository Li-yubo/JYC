import yaml
from typing import Dict
from FileHandler import FileHandler
class YamlHandler(FileHandler):
    """YAML file handler"""
    def read_file(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def write_file(self, data: Dict) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)
