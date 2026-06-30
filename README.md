# **HOA Auditor Agent**

A multi-agent auditing system built using the Google Agent Development Kit (ADK) framework and gemini-2.5-flash natively to audit Homeowner Association (HOA) legal and financial documents.

## **💡 Core Business Value & Problem Space**

Reviewing Homeowner Association (HOA) documentation is one of the highest-friction steps in a real estate transaction. Buyers are routinely handed massive, unorganized text dumps spanning 300+ pages of complex legal jargon. Hidden inside this noise are critical liabilities—such as structural funding deficits, outstanding accounts payable, or strict property restrictions—that can lead to immediate buyer regret or stall mortgage timelines entirely.

This application acts as a compliance guardrail, ensuring that real estate professionals and homebuyers can evaluate property risk safely while systematically cross-referencing files against state-level mandates.

## **🛠️ Key Architectural & Product Features**

* **LLM Core & ADK Routing:** Powered by gemini-2.5-flash utilizing the Google ADK framework to route specialized tasks seamlessly across an executive synthesizer root agent, a financial specialist, and a legal specialist.  
* **The Token Blocker (Cost Insulation Caching Layer):** Implements a robust cryptographic fingerprinting system linked to a **Supabase** backend. When a document package is analyzed, a unique MD5 text hash is generated. Identical packages bypass live LLM generation completely, delivering instant results from the database cache at **0 token cost** and near-zero latency, protecting the application's operating margins.  
* **State Compliance Guardrails:** The application explicitly cross-references data against a formal state regulation framework (such as Washington State's WUCIOA RCW 64.90.640). It verifies that every statutory disclosure requirement a seller is legally mandated to provide is present, automatically flagging missing items as critical legal vulnerabilities.  
* **Real-World Data Ingestion Flexibility:** Built with a variable-input ingestion layer that handles diverse condo disclosure packages seamlessly—whether a specific building provides 5 massive text blocks or 15 highly atomized documents.  
* **Interactive Frontend Experience:** A clean, multi-tab **Streamlit** dashboard that pulls the cached data directly from Supabase, rendering actionable checklists, urgent legal/financial risk cards, and explicit source anchors for buyers.

## **🛠️ Installation & Setup**

Follow these steps to get the environment and multi-agent pipeline running locally.

### **Prerequisites**

Ensure you have Python 3.11+ and uv installed on your machine:

\# Install uv if it is not already installed  
curl \-LsSf \[https://astral.sh/uv/install.sh\](https://astral.sh/uv/install.sh) | sh

### **Local Configuration**

1. **Clone the Repository:**  
   git clone \[https://github.com/layclough/kaggle\_submission\_hoa\_auditor.git\](https://github.com/layclough/kaggle\_submission\_hoa\_auditor.git)  
   cd kaggle\_submission\_hoa\_auditor

2. **Configure Environment Variables:**  
   Create a .env file inside the app/ directory matching the blueprint provided in app/.env.example:  
   GEMINI\_API\_KEY=your\_gemini\_api\_key\_here  
   SUPABASE\_URL=your\_supabase\_project\_url\_here  
   SUPABASE\_KEY=your\_supabase\_anon\_public\_key\_here

3. **Sync the Virtual Environment:**  
   Compile the exact lockfile and install all project dependencies instantly inside a local sandbox using uv:  
   uv sync

## **🚀 Running the Application**

To spin up the interactive Streamlit dashboard locally, execute the following command from the root project folder:

PYTHONPATH=. uv run streamlit run app/ui.py

Once executed, your terminal will provide a local URL (typically http://localhost:8501) to open and view the application directly in your web browser.

## **📂 Project Structure**

.  
├── README.md  
├── agents.json                        \# Core agents definition/discovery configuration  
├── pyproject.toml                     \# Project packaging and dependencies  
├── uv.lock                            \# Fully resolved project lockfile  
├── app/  
│   ├── \_\_init\_\_.py                    \# Initializes the ADK App  
│   ├── agent.py                       \# Defines executive\_synthesizer (Root), financial\_specialist, legal\_specialist  
│   ├── ui.py                          \# Streamlit frontend user interface dashboard  
│   ├── supabase\_client.py             \# Supabase token-blocker database interaction client  
│   ├── tools.py                       \# Registers HOA tools for the ADK agents  
│   └── .env.example                   \# Generic environment variable blueprint (Safe to commit)  
├── system/  
│   └── schemas/  
│       └── report\_manifest.yaml       \# Report Schema v2.0 validation manifest  
├── tools/  
│   ├── \_\_init\_\_.py  
│   └── hoa\_tools.py                   \# Implements tool functions (read\_mcp\_document\_chunk, validate\_cross\_reference)  
└── tests/  
    └── eval/  
        ├── eval\_config.yaml           \# Day 4 evaluation config (metrics & thresholds)  
        └── datasets/  
            └── basic-dataset.json     \# Day 4 evaluation test cases  
