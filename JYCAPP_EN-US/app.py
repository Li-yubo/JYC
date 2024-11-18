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

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        source_file = os.path.join(os.path.dirname(__file__), 'styles_config.ini')
        target_file = os.path.join(target_dir, 'styles_config.ini')
        copyfile(source_file, target_file)
def print_examples():
    print('''Usage Examples:
  # Retrieve Data
  python jyc data.json -g -k "users[0].name"              # Get the first user's name
  python jyc data.json -g -k "users[*].age"               # Get all users' ages
  python jyc data.json -g -k "users[?age>=18].name"       # Get names of adult users
  python jyc data.json -g -k "users[?name~=^J].email"     # Get emails of users whose names start with J
  python jyc data.json -g -k "users..name"                # Recursively get all name fields
  python jyc data.json -g -k "users[1:3]"                 # Get users from index 1 to 3
  python jyc data.json -g -k "items[*].price@sum"         # Calculate sum of all item prices
  python jyc data.json -g -k "items@sort(price)"          # Sort items by price

  # Modify Data
  python jyc data.json -s -k "users[0].age" -v 25        # Modify first user's age
  
  # Add Data
  python jyc data.json -a -k "users" -ak "2" -v '{"name":"Tom","age":20}'  # Add new user
  
  # Delete Data
  python jyc data.json -d -k "users[0]"                  # Delete first user
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
    raise ValueError(f"Unsupported file type: {file_type}")

def main():
    post_install()
    parser = argparse.ArgumentParser(
        description='''File Operation Tool - JYC - Supports operations on JSON, YAML, and INI configuration files.
Supports complex query syntax including array indexing, condition filtering, recursive search, sorting, and aggregation.''',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('file', nargs='?',
                       help='File path to operate on (supports .json, .yaml)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', '-a', action='store_true', 
                      help='Add new data')
    group.add_argument('--delete', '-d', action='store_true', 
                      help='Delete specified data')
    group.add_argument('--set', '-s', action='store_true', 
                      help='Modify existing data')
    group.add_argument('--get', '-g', action='store_true', 
                      help='Retrieve data')
    group.add_argument('--examples', '-e', action='store_true',
                      help='Show usage examples')
    
    parser.add_argument('--key', '-k', required=False, 
                       help='Data access path, supports complex query syntax')
    parser.add_argument('--addkey', '-ak', 
                       help='Key name or array index for add operation')
    parser.add_argument('--value', '-v', 
                       help='Value to set or add')
    parser.add_argument('--pretty', '-p', action='store_true', 
                       help='Beautify output and smart type conversion (non-string)')
    
    args = parser.parse_args()

    if args.examples:
        print_examples()
        return

    if not args.file:
        parser.error("File path is required unless using --examples/-e option")

    try:
        handler = get_file_handler(args.file)
        
        if args.get:
            success, value = handler.get_value(args.key, args.pretty)
            if success:
                print(f"Value at {args.key}:\n {value}")
            else:
                print(f'Key {args.key} not found')
                exit(1) 
                
        elif args.add :
            if not args.value or not args.addkey:
                parser.error("--value and --addkey are required for add operation")
            success = handler.add_value(args.key, args.addkey, args.value, args.pretty)
            print(f"Successfully {'added' if args.add else 'changed'} value at {args.key}" if success else "Operation failed")
            if not success:
                exit(1)
        elif args.set:
            if not args.value:
                parser.error("-value is required for set operation")
            success = handler.set_value(args.key, args.value, args.pretty)
            print(f"Successfully {'added' if args.add else 'changed'} value at {args.key}" if success else "Operation failed")            
            if not success:
                exit(1)
        elif args.delete:
            success = handler.delete_value(args.key)
            print(f"Successfully deleted value at {args.key}" if success else f"Key {args.key} not found")
            if not success:
                exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()