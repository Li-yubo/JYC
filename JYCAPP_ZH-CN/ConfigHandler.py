import configparser
from typing import  Dict
from FileHandler import FileHandler
class ConfigHandler(FileHandler):
    """CONFIG(INI)文件处理器"""
    def read_file(self) -> Dict:
        config = configparser.ConfigParser()
        try:
            config.read(self.file_path, encoding='utf-8')
            return {section: dict(config[section]) for section in config.sections()}
        except:
            return {}

    def write_file(self, data: Dict) -> None:
        config = configparser.ConfigParser()
        for section, values in data.items():
            config[section] = values
        with open(self.file_path, 'w', encoding='utf-8') as f:
            config.write(f)
