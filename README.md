# Logeion MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Server](https://img.shields.io/badge/MCP-Server-green.svg)](https://modelcontextprotocol.io/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-orange.svg)](https://spacy.io/)

Logeion is a powerful dictionary for Ancient Latin and Greek, now available as an MCP (Model Context Protocol) server so that LLMs can interact with the dictionary functionality.

## 🌟 Features

- **Latin Dictionary Lookup**: Search for Latin words with comprehensive definitions
- **Lemmatization Support**: Automatically finds word lemmas using spaCy's Latin language model
- **SQLite Database**: Fast, local database access for quick word lookups
- **MCP Integration**: Seamlessly integrates with MCP-compatible clients and LLMs

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/logeion-mcp-server.git
cd logeion-mcp-server

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download la_core_web_lg

# Run the server
python logeion.py
```

## 📚 Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/logeion-mcp-server.git
cd logeion-mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the Latin language model for spaCy:
```bash
python -m spacy download la_core_web_lg
```

5. Download the database file:
   - The database file `dvlg-wheel-mini.sqlite` should be placed in the project root directory
   - This contains the Latin dictionary entries

## 🛠️ Usage

### Running the MCP Server

```bash
python logeion.py
```

The server runs on stdio transport by default, making it compatible with MCP clients.

### MCP Tools

#### `get_word(word: str)`

Searches for a Latin word in the dictionary database.

**Parameters:**
- `word` (str): The Latin word to search for

**Returns:**
- `success` (bool): Whether the search was successful
- `word` (str): The original search term
- `lemma` (str, optional): The lemmatized form if found
- `results` (list, optional): Database results if found
- `method` (str): How the search was performed ("exact_match", "lemmatized", "none", "error")
- `error` (str, optional): Error message if something went wrong

**Example Usage:**
```python
# Search for "amare" (to love)
result = get_word("amare")

# Search for "amo" (I love) - will find the lemma "amare"
result = get_word("amo")
```

### Database Schema

The server connects to a SQLite database with the following structure:
- **Table**: `Entries`
- **Key Column**: `head` - contains the Latin word forms
- **Additional columns**: Various dictionary information (definitions, parts of speech, etc.)

## 🧪 Testing & Demo

### Run Tests
```bash
python test_logeion.py
```

### Run Demo
```bash
python demo.py
```

### Explore Database
```bash
python explore_db.py
```

## 🐳 Docker Deployment

### Quick Start with Docker
```bash
# Build and run
docker-compose up --build

# Or build manually
docker build -t logeion-mcp-server .
docker run -it --rm -v $(pwd)/dvlg-wheel-mini.sqlite:/app/dvlg-wheel-mini.sqlite:ro logeion-mcp-server
```

## 🏗️ Development

### Project Structure

```
logeion-mcp-server/
├── logeion.py          # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── LICENSE            # MIT License
├── mcp-config.json    # MCP server configuration
├── demo.py            # Demo script
├── test_logeion.py    # Comprehensive test suite
├── explore_db.py      # Database exploration utility
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
└── venv/              # Virtual environment
```

### Adding New Tools

To add new MCP tools, use the `@mcp.tool()` decorator:

```python
@mcp.tool()
def your_new_tool(param1: str, param2: int):
    # Your tool implementation
    return {"result": "success"}
```

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Comprehensive deployment instructions
- **[MCP Configuration](mcp-config.json)** - Server configuration and metadata
- **[API Reference](README.md#mcp-tools)** - Tool documentation and examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run linting
flake8 .
black --check .
isort --check-only .

# Run tests with coverage
pytest test_logeion.py --cov=logeion
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [Report bugs and feature requests](https://github.com/philipaidanbooth/logeion-mcp-server/issues)
- **Discussions**: [Join the conversation](https://github.com/philipaidanbooth/logeion-mcp-server/discussions)
- **Documentation**: Check this README and the [MCP documentation](https://modelcontextprotocol.io/)

## 🌐 Community & Social

- **GitHub**: [Repository](https://github.com/philipaidanbooth/logeion-mcp-server)
- **MCP Hub**: [Server Listing](https://mcp.hub) (coming soon)
- **Twitter**: [@YourHandle](https://twitter.com/PhilipB77106613) (if available)

## 🙏 Acknowledgments

- Built with the [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) framework
- Uses [spaCy](https://spacy.io/) for Latin language processing
- Integrates with the Logeion Latin dictionary database
- Inspired by classical language education and digital humanities

---

**Note**: This MCP server provides access to Latin dictionary functionality through the Model Context Protocol, enabling LLMs to perform Latin word lookups and analysis.

**Made with ❤️ for the classical language community**
