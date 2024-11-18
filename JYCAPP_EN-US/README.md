# JYC - Advanced File Content Operation Tool

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Blog](https://img.shields.io/badge/blog-www.yubo.ltd-orange.svg)](http://www.yubo.ltd/)

JYC is an advanced file content operation tool designed for developers to efficiently perform file data querying, modification, addition, and deletion operations. The tool supports multiple file formats, including JSON, YAML, and configuration files, providing a powerful command-line interface for handling complex data operation requirements.

## Features

- í ½í³ Support for multiple file formats (JSON, YAML, Config files)
- í ½í´ Powerful query functionality with complex expression support
- âï¸ Support for data addition, modification, and deletion
- í ¼í¾¨ Formatted output for better readability
- í ½í» ï¸ Advanced path expression support, including index access, conditional filtering, recursive search, etc.

## Tech Stack

- Python 3.x
- Pygments: For formatted color text output
- JSON, YAML: For handling different types of data files

## Installation

Ensure you have Python 3 and pip installed on your system. Then follow these steps:

```bash
# Clone repository
git clone https://github.com/Li-yubo/JYC.git
cd JYC

# Install dependencies
pip install -r requirements.txt
```

## Usage

Use the command-line interface for operations:

```bash
python app.py <file> --key <key_path> [options]
```

### Options

- `--add, -a`: Add new data to specified key
- `--delete, -d`: Delete data at specified key
- `--set, -s`: Modify data at specified key
- `--get, -g`: Get data from specified key
- `--key, -k`: Specify operation key path
- `--addkey, -ak`: Specify key or index for add operation
- `--value, -v`: Specify value for add or modify operations
- `--pretty, -p`: Output formatted data

### Advanced Path Expressions

The tool supports various advanced path expressions:
- `items[0]`: Access array index
- `items[*]`: Access all array elements
- `items[?class=web]`: Conditional filtering
- `items[?name~=^test]`: Regex matching
- `items..name`: Recursive search
- `items[1:3]`: Slice operation
- `items[*].price@sum`: Aggregation operation
- `items@sort(price)`: Sorting operation

### Examples

Get specific data from JSON file:

```bash
python app.py example.json --get -k "items[?name=='example'].value"
```

Add new data to JSON file:

```bash
python app.py example.json --add -k "items" --addkey "newKey" --value "{\"new\":\"data\"}" -p
```

Modify existing data:

```bash
python app.py example.json --set -k "items[0].name" --value "newName" -p
```

Delete data:

```bash
python app.py example.json --delete -k "items[0]"
```

## Development

The project consists of three main components:
- `app.py`: Main entry point and command-line interface
- `FileHandler.py`: Base class for file operations
- `getValue.py`: Core logic for path expression parsing and evaluation

## Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create your feature branch
3. Submit a Pull Request

## About the Author

- Blog: [www.yubo.ltd](http://www.yubo.ltd/)
- GitHub: [Li-yubo](https://github.com/Li-yubo)



## Acknowledgments

Thanks to all contributors who have helped make this project better!

---

If you find this project helpful, please give it a star â­ï¸

[View more project details](https://github.com/Li-yubo/JYC)

## Future Enhancements

- Support for more file formats
- Enhanced error handling and reporting
- Performance optimizations
- GUI interface
- API integration capabilities

For more information and updates, visit the [project repository](https://github.com/Li-yubo/JYC).

