import argparse
import json
import yaml
import configparser
from pathlib import Path
from FileHandler import FileHandler
from JsonHandler import JsonHandler
from YamlHandler import YamlHandler
from ConfigHandler import ConfigHandler

import os
from shutil import copyfile

def post_install():
    home_dir = os.path.expanduser("~")
    target_dir = os.path.join(home_dir, ".jyc")

    # 创建目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

        # 复制文件
        source_file = os.path.join(os.path.dirname(__file__), 'styles_config.ini')
        target_file = os.path.join(target_dir, 'styles_config.ini')
        copyfile(source_file, target_file)


def print_examples():
    print('''使用示例:
  # 获取数据
  python jyc data.json -g -k "users[0].name"              # 获取第一个用户的名字
  python jyc data.json -g -k "users[*].age"               # 获取所有用户的年龄
  python jyc data.json -g -k "users[?age>=18].name"       # 获取成年用户的名字
  python jyc data.json -g -k "users[?name~=^J].email"     # 获取名字以 J 开头的用户的电子邮件
  python jyc data.json -g -k "users..name"                # 递归获取所有名字字段
  python jyc data.json -g -k "users[1:3]"                 # 获取索引1到3的用户
  python jyc data.json -g -k "items[*].price@sum"         # 计算所有商品价格的总和
  python jyc data.json -g -k "items@sort(price)"          # 按价格排序商品

  # 修改数据
  python jyc data.json -s -k "users[0].age" -v 25        # 修改第一个用户的年龄
  
  # 添加数据
  python jyc data.json -a -k "users" -ak "2" -v '{"name":"Tom","age":20}'  # 添加新用户
  
  # 删除数据
  python jyc data.json -d -k "users[0]"                  # 删除第一个用户
''')
def detect_file_type(file_path: str) -> str:
    """检测文件类型"""
    if not Path(file_path).is_file():
        return "unknown"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        try:
            json.loads(content)
            return "json"
        except json.JSONDecodeError:
            pass
        
        try:
            yaml.safe_load(content)
            return "yaml"
        except yaml.YAMLError:
            pass
        
        try:
            parser = configparser.ConfigParser()
            parser.read_string(content)
            return "config"
        except configparser.Error:
            pass
        
        return "unknown"
    except Exception:
        return "unknown"

def get_file_handler(file_path: str) -> FileHandler:
    """获取对应的文件处理器"""
    file_type = detect_file_type(file_path)
    handlers = {
        "json": JsonHandler,
        "yaml": YamlHandler,
        "config": ConfigHandler
    }
    handler_class = handlers.get(file_type)
    if handler_class:
        return handler_class(file_path)
    raise ValueError(f"未知文件类型: {file_type}")

def main():
    post_install()
    parser = argparse.ArgumentParser(
        description='''文件操作工具 - JYC - 支持对 JSON、YAML 和 INI 配置文件的操作。
支持复杂的查询语法，包括数组索引、条件过滤、递归搜索、排序和聚合。''',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('file', nargs='?', help='操作文件的路径（支持 .json、.yaml）')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', '-a', action='store_true', help='添加新数据')
    group.add_argument('--delete', '-d', action='store_true', help='删除指定数据')
    group.add_argument('--set', '-s', action='store_true', help='修改现有数据')
    group.add_argument('--get', '-g', action='store_true', help='检索数据')
    group.add_argument('--examples', '-e', action='store_true', help='显示使用示例')
    
    parser.add_argument('--key', '-k', required=False, help='数据访问路径，支持复杂的查询语法')
    parser.add_argument('--addkey', '-ak', help='添加操作的键名或数组索引')
    parser.add_argument('--value', '-v', help='设置或添加的值')
    parser.add_argument('--pretty', '-p', action='store_true', help='美化输出并智能类型转换（非字符串）')
    
    args = parser.parse_args()

    if args.examples:
        print_examples()
        return

    if not args.file:
        parser.error("操作文件路径是必需的，除非使用 --examples/-e 选项查看示例")

    try:
        handler = get_file_handler(args.file)
        # 如果指定了 examples，直接显示示例并退出
        # 检查其他操作是否有必要的参数


        if args.get:
            success, value = handler.get_value(args.key, args.pretty)
            if success:
                print(f"Value at {args.key}:\n {value}")
            else:
                print(f'Key {args.key} 没有找到')
                exit(1) 
                
        elif args.add :
            if not args.value or not args.addkey:
                parser.error("--value 是添加操作所必需的")
                parser.error("--addkey 是添加操作所必需的")
            success = handler.add_value(args.key, args.addkey, args.value, args.pretty)
            print(f"成功添加 value at {args.key}" if success else "操作失败")
            if not success:
                exit(1)
        elif args.set:
            if not args.value:
                parser.error("--value 是修改操作所必需的")
            success = handler.set_value(args.key, args.value, args.pretty)
            print(f"成功修改 value at {args.key}" if success else "操作失败")            
            if not success:
                exit(1)
        elif args.delete:
            success = handler.delete_value(args.key)
            print(f"成功删除 value at {args.key}" if success else f"Key {args.key} 没有找到")
            if not success:
                exit(1)

    except Exception as e:
        print(f"失败: {str(e)}")

if __name__ == '__main__':
    main()