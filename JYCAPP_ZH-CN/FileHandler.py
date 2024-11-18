import json
from typing import Any, Dict, Union, List
import re
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer
from getValue import getValue
import os


class FileHandler:
    """文件处理基类"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.read_file()
        
    def read_file(self) -> Union[Dict, None]:
        raise NotImplementedError

    def write_file(self, data: Dict) -> None:
        raise NotImplementedError
    
            
    def get_value(self, key_path: str, pretty: bool = True) -> Any:
        gv = getValue(key_path)
        gv.get = True
        gv.valueGet(self.data)
        if pretty:
            return gv.SETADD, self.pretty_print(gv.GETARR)
        return gv.SETADD, gv.GETARR
    
    def set_value(self, key_path: str, value, pretty: bool = True) -> Any:
        gv = getValue(key_path)
        gv.set = True
        if pretty:
            value = self.pretty_value(value)
        gv.SETADDVAL = value
        gv.valueGet(self.data)
        self.write_file(self.data)
        return gv.SETADD        

    def add_value(self, key_path: str, addkey, value, pretty: bool = True) -> Any:
        gv = getValue(key_path)
        gv.add = True
        if pretty:
            value = self.pretty_value(value)
        gv.SETADDVAL = value
        gv.SETADDKEY = addkey
        gv.valueGet(self.data)
        self.write_file(self.data)
        
        return gv.SETADD        

    def delete_value(self, key_path: str) -> Any:
        gv = getValue(key_path)
        gv.delete = True
        gv.valueGet(self.data)
        self.write_file(self.data)
        return gv.SETADD        

    
    def pretty_print(self, data: Any) -> str:
        """格式化输出带颜色的JSON"""
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        # 获取当前文件的目录
        current_dir = os.path.expanduser("~")
        style_config = StyleConfig(current_dir)
        # 获取当前活动的样式
        current_style = style_config.get_active_style()        
        return highlight(json_str, JsonLexer(), Terminal256Formatter(style=current_style))        
        

    def pretty_value(self, value):
        # 尝试转换为整数
        try:
            return int(value)
        except ValueError:
            pass

        # 尝试转换为浮点数
        try:
            return float(value)
        except ValueError:
            pass

        # 尝试转换为布尔值
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'

        # 尝试转换为复数
        try:
            return complex(value)
        except ValueError:
            pass

        # 尝试解析为JSON（可能是列表、字典等）
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # 如果所有尝试都失败了，返回原始字符串
        return value
    
    
    
class StyleConfig:
    def __init__(self, current_dir):
        self.config_file = f'{current_dir}/.jyc/styles_config.ini'
        self.default_style = 'monokai'
    
    def get_active_style(self):
        """获取第一个未被注释的样式"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith('style'):
                        return line.split('=')[1].strip()
        except Exception as e:
            #print(f"配置文件读取错误: {e}")
            return self.default_style
        
        return self.default_style    