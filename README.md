### AI_Ledger
### Overview

AI_Ledger is an AI-powered personal expense tracking system.
It combines FastAPI, MySQL, and Google Agent Development Kit (ADK) to provide a chat-based interface for recording, modifying, and reporting financial transactions.

With natural language input, you can:

Record new expenses ("Starbucks 5 today")

Modify existing records ("Change Starbucks today to 8")

Generate reports ("How much did I spend this week?")

### Features

Natural Language Input – add and edit records with plain English.

AI-Powered Classification – categories (e.g. Food, Shopping, Transport) are auto-detected by LLM instead of hard-coded mapping.

Flexible Reporting – generate reports by:

time range (today, yesterday, last week, month, year)

category filters

Database-backed – records stored in MySQL with normalized schema.

Web UI – simple frontend built with HTML/CSS + FastAPI serving APIs.

Extensible – designed with sub-agents (create/modify/report) that can be extended later (e.g. invoice upload).

### Tech Stack

Backend: Python 3.11, FastAPI, Uvicorn

Database: MySQL 

AI Agent: Google ADK (Gemini 2.0 Flash)

Frontend: HTML + CSS (chat interface)

Deployment: AWS EC2


### Demo Video

[(https://img.youtube.com/vi/k412a6EeWvI/0.jpg)](https://youtu.be/k412a6EeWvI)

### Quick Start
### 1. Clone the repo
```bash
git clone git@github.com:xinbofan23/ai_ledger.git
cd ai_ledger
```

### 2. Setup environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file:
```env
GOOGLE_API_KEY=your_api_key_here
DB_HOST=127.0.0.1
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=ledger
```

### 4. Run locally
```bash
uvicorn api:app --host 0.0.0.0 --port 9876 --reload
```
