<<<<<<< HEAD
# Smart_Contract_Auditor-AI
=======
# LLM-Based Smart Contract Vulnerability Scanner

This project is a complete smart contract vulnerability scanner that uses Large Language Models (LLMs) to analyze Solidity smart contracts and identify potential security vulnerabilities. The system combines both AI-driven analysis and rule-based pattern matching to provide comprehensive security insights.

## Features

- LLM-powered smart contract analysis
- Detection of common vulnerabilities (reentrancy, overflows, access control issues, etc.)
- Severity classification of vulnerabilities
- Detailed explanations and recommendations
- Line number references for easier debugging
- Easy-to-use web interface
- Dockerized deployment for easy setup

## Project Structure

```
smart-contract-scanner/
├── backend/
│   ├── app.py                  # Flask backend API
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend Docker configuration
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── styles.css              # CSS styling
│   ├── script.js               # Frontend JavaScript
│   ├── nginx.conf              # Nginx configuration
│   └── Dockerfile              # Frontend Docker configuration
└── docker-compose.yml          # Docker Compose configuration
```

## Installation and Setup

### Prerequisites

- Docker and Docker Compose
- 4GB+ RAM for running the LLM
## Installation and Setup

### Prerequisites

- Docker and Docker Compose
- 4GB+ RAM for running the LLM

### Getting Started

1. Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/smart-contract-scanner.git
cd smart-contract-scanner
```

2. Create the directory structure and files:

```bash
mkdir -p backend
mkdir -p frontend
```

3. Copy the provided files into their respective directories.

4. Build and start the Docker containers:

```bash
docker-compose up -d
```

5. The application will be available at http://localhost

### Using Your Own Model

By default, the system uses the `gpt2` model from Hugging Face, but it's designed to work with any fine-tuned model specialized for smart contract vulnerability detection.

To use your own model:

1. Fine-tune a model on a dataset of vulnerable and secure smart contracts.
2. Update the MODEL_PATH environment variable in docker-compose.yml:

```yaml
environment:
  - MODEL_PATH=/path/to/your/model
```

## Usage

1. Access the web interface at http://localhost
2. Enter or paste your Solidity smart contract code in the editor
3. Click "Scan for Vulnerabilities"
4. Review the analysis results, which include:
   - An overview of detected vulnerabilities
   - Severity counts (high, medium, low)
   - Detailed explanations of each vulnerability
   - Recommendations for fixing the issues

## API Endpoints

The backend provides the following REST API endpoints:

- `POST /api/scan`: Scans a smart contract for vulnerabilities
  - Request body: `{ "contract_code": "your contract code here" }`
  - Returns: JSON with vulnerability analysis

- `GET /api/health`: Health check endpoint
  - Returns: Status information about the running model

## Future Improvements

- Implement user authentication
- Add support for multiple file analysis
- Create a vulnerability knowledge base
- Integrate with blockchain explorers for deployed contract analysis
- Add PDF report generation
- Support for Vyper and other smart contract languages
- Integration with development environments (VSCode extension, etc.)

## For Production Use

Before deploying this system to production:

1. Replace the default model with a properly fine-tuned LLM for smart contract security
2. Add proper authentication and rate limiting
3. Consider using a more robust database for storing scan results
4. Implement HTTPS with proper certificates
5. Consider using a managed Kubernetes service for better scalability

## Disclaimer

This tool is designed to assist in identifying potential vulnerabilities, but it should not replace a comprehensive security audit by blockchain security experts. Some vulnerabilities may not be detected, and false positives may occur.

## License

MIT
>>>>>>> ee22ed9 (Initial commit)
