# JYC - 高级文件内容操作工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Blog](https://img.shields.io/badge/blog-www.yubo.ltd-orange.svg)](http://www.yubo.ltd/)

JYC 是一个高级文件内容操作工具，专为开发者设计，以便于他们能够高效地进行文件数据的查询、修改、添加和删除操作。该工具支持多种文件格式，包括 JSON、YAML 和配置文件，提供了一个强大的命令行界面来处理复杂的数据操作需求。

## 注意事项

- ⚠️ 所有配置文件中不可有注释，若有注释将会被删除注释，有需要的请copy一份带注释的原文件
- ⚠️ json文件绝对不能有注释!!!带有注释的json文件格式将会发生变化

## 特性

- 📂 支持多种文件格式（JSON, YAML, 配置文件）
- 🔍 强大的查询功能，支持复杂的查询表达式
- ✏️ 支持数据的添加、修改和删除
- 🎨 支持格式化输出，使数据更易读
- 🛠️ 高级路径表达式支持，包括索引访问、条件过滤、递归查找等

## 技术栈

- Python 3.x
- Pygments：用于输出格式化的彩色文本
- JSON, YAML：用于处理不同类型的数据文件

## 安装

确保你的系统中已安装 Python 3 和 pip。然后执行以下步骤：

```bash
# 克隆仓库
git clone https://github.com/Li-yubo/JYC.git
cd JYC

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

使用命令行界面进行操作，具体命令如下：

```bash
python app.py <file> --key <key_path> [options]
```

### 选项

- `--add, -a`：添加新数据到指定键
- `--delete, -d`：删除指定键的数据
- `--set, -s`：修改指定键的数据
- `--get, -g`：获取指定键的数据
- `--key, -k`：指定操作的键路径
- `--addkey, -ak`：添加操作时指定的键或索引
- `--value, -v`：指定添加或修改的值
- `--pretty, -p`：输出格式化的数据

### 示例

获取 JSON 文件中的特定数据：

```bash
python app.py example.json --get -k "items[?name=='example'].value"
```

添加新数据到 JSON 文件：

```bash
python app.py example.json --add -k "items" --addkey "newKey" --value "{\"new\":\"data\"}" -p
```

## 贡献

欢迎提交 Pull Request 或创建 Issue！

## 关于作者

- 博客：[www.yubo.ltd](http://www.yubo.ltd/)
- GitHub：[Li-yubo](https://github.com/Li-yubo)



## 致谢

感谢所有为这个项目做出贡献的开发者！

---

如果觉得这个项目有帮助，欢迎 star ⭐️

[查看更多项目详情](https://github.com/Li-yubo/JYC)
