# HOA Auditor Agent

A multi-agent auditing system built using the Google Agent Development Kit (ADK) framework and `gemini-2.5-flash` natively to audit Homeowner Association (HOA) legal and financial documents.

## Project Structure

```
.
├── README.md
├── agents.json                        # Core agents definition/discovery configuration
├── pyproject.toml                     # Project packaging and dependencies
├── app/
│   ├── __init__.py                    # Initializes the ADK App
│   ├── agent.py                       # Defines executive_synthesizer (Root), financial_specialist, legal_specialist
│   ├── tools.py                       # Registers HOA tools for the ADK agents
│   └── .env                           # Environment configuration
├── system/
│   └── schemas/
│       └── report_manifest.yaml       # Report Schema v2.0 validation manifest
├── tools/
│   ├── __init__.py
│   └── hoa_tools.py                   # Implements mock tool functions (read_mcp_document_chunk, validate_cross_reference)
└── tests/
    └── eval/
        ├── eval_config.yaml           # Day 4 evaluation config (metrics & thresholds)
        └── datasets/
            └── basic-dataset.json     # Day 4 evaluation test cases
```

## Setup & Running locally

Install the project dependencies using `uv` or `pip`:
```bash
uv sync
```

## Running Evaluation (Day 4)

To run inference and grade the agent locally against the test dataset:
```bash
agents-cli eval run
```
or run them in two steps:
```bash
agents-cli eval generate
agents-cli eval grade
```
