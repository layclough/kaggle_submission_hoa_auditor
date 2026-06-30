# HOA Auditor Agent

A multi-agent auditing system built using the Google Agent Development Kit (ADK) framework and `gemini-2.5-flash` natively to audit Homeowner Association (HOA) legal and financial documents.

## 💡 Core Business Value & Problem Space
Reviewing Homeowner Association (HOA) documentation is one of the highest-friction steps in a real estate transaction. Buyers are routinely handed massive, unorganized text dumps spanning 300+ pages of complex legal jargon. Hidden inside this noise are critical liabilities—such as structural funding deficits, outstanding accounts payable, or strict property restrictions—that can lead to immediate buyer regret or stall mortgage timelines entirely.

This application acts as a compliance guardrail, ensuring that real estate professionals and homebuyers can evaluate property risk safely while systematically cross-references files against state-level mandates.

## 🛠️ Key Architectural & Product Features

* **LLM Core & ADK Routing:** Powered by `gemini-2.5-flash` utilizing the Google ADK framework to route specialized tasks seamlessly across an executive synthesizer root agent, a financial specialist, and a legal specialist.
* **The Token Blocker (Cost Insulation Caching Layer):** Implements a robust cryptographic fingerprinting system linked to a **Supabase** backend. When a document package is analyzed, a unique MD5 text hash is generated. Identical packages bypass live LLM generation completely, delivering instant results from the database cache at **0 token cost** and near-zero latency, protecting the application's operating margins.
* **State Compliance Guardrails:** The application explicitly cross-references data against a formal state regulation framework (such as Washington State's WUCIOA RCW 64.90.640). It verifies that every statutory disclosure requirement a seller is legally mandated to provide is present, automatically flagging missing items as critical legal vulnerabilities.
* **Real-World Data Ingestion Flexibility:** Built with a variable-input ingestion layer that handles diverse condo disclosure packages seamlessly—whether a specific building provides 5 massive text blocks or 15 highly atomized documents.

## Project Structure

```text
.
├── README.md
├── agents.json                        # Core agents definition/discovery configuration
├── pyproject.toml                     # Project packaging and dependencies
├── app/
│   ├── __init__.py                    # Initializes the ADK App
│   ├── agent.py                       # Defines executive_synthesizer (Root), financial_specialist, legal_specialist
│   ├── tools.py                       # Registers HOA tools for the ADK agents
│   └── .env                           # Environment configuration (git-ignored)
├── system/
│   └── schemas/
│       └── report_manifest.yaml       # Report Schema v2.0 validation manifest
├── tools/
│   ├── __init__.py
│   └── hoa_tools.py                   # Implements tool functions (read_mcp_document_chunk, validate_cross_reference)
└── tests/
    └── eval/
        ├── eval_config.yaml           # Day 4 evaluation config (metrics & thresholds)
        └── datasets/
            └── basic-dataset.json     # Day 4 evaluation test cases