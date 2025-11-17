# AI-Agent-Framework-Tutorial-Sales-Report-Automation

This project demonstrates how to use the Microsoft Agent Framework to build AI-powered workflows for data analysis and reporting.

## Prerequisites

- Python 3.12 or higher
- Windows OS (if you are using the provided batch file)

## Installation

### 1. Set Up Virtual Environment

Run the setup batch file to create and configure the virtual environment:

```cmd
setup_venv.bat
```

This will:
- Create a virtual environment named `agentframework`
- Activate the environment
- Install all required dependencies from `requirements.txt`

### 2. Configure Environment Variables

Create a `.env` file in the project root with your Azure OpenAI credentials:

```env
API_KEY=your_azure_openai_api_key
AZURE_AI_MODEL_DEPLOYMENT_NAME=your_deployment_name
AZURE_AI_PROJECT_ENDPOINT=your_endpoint_url
AZURE_AI_API_VERSION=your_api_version
```

## Running the Application

### Activate the Environment (if not already active)

```cmd
call agentframework\Scripts\activate
```

### Run the Test Script

```cmd
python main.py
```

This will:
- Analyze the sample sales data from `sample_sales_data.csv`
- Generate a comprehensive sales report using a multi-agent workflow
- Display the conversation between the data analyzer and report writer agents

## What the Script Does

The `main.py` script demonstrates a sequential agent workflow:

1. **Data Analyzer Agent**: Reads CSV data and calculates key statistics (revenue, top performers, etc.)
2. **Report Writer Agent**: Transforms the data into a stakeholder-friendly report

This is useful for automating daily sales summaries for managers, executives, and team leads in various contexts (restaurants, retail, e-commerce, etc.).

## Project Structure

```
.
├── agentframework/          # Virtual environment (created by setup_venv.bat)
├── main.py                 # Main sales report workflow demo
├── sample_sales_data.csv    # Sample data for testing
├── requirements.txt         # Python dependencies
├── setup_venv.bat          # Environment setup script
└── README.md               # This file
```

## Deactivating the Environment

When you're done working, deactivate the virtual environment:

```cmd
deactivate
```
