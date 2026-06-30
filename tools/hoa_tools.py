"""Custom tools for auditing Homeowner Association (HOA) documents.

Simulates document retrieval and cross-reference validation based on Supabase aggregates.
"""

#from google.adk.tools import ToolContext

# Mock document repository for simulation
MOCK_DOCUMENTS = {
    "financials.txt": {
        0: "MONTHLY HOA MAINTENANCE FEE: $450.00 per unit, due on the 1st of each month.\n"
           "RESERVE FUNDING STATUS: Current reserve balance is $120,000. Reserve Study recommends a balance of $400,000.\n"
           "The reserves are currently 30% funded (underfunded by $280,000).",
        1: "PENDING ASSESSMENTS: A special assessment of $5,000.00 per unit is pending for roofing repairs, "
           "expected to be voted on during the upcoming Q3 board meeting."
    },
    "ccrs.txt": {
        0: "Section 4.2 (Assessments): The Board of Directors shall have the power to levy special assessments "
           "for capital improvements or repairs, provided that any assessment exceeding $1,000 per unit "
           "requires a majority vote of the members.\n"
           "Section 7.1 (Leasing Restrictions): No unit may be leased for a period of less than 30 days. "
           "A maximum of 15% of all units in the community may be leased at any single time (Lease Cap).",
        1: "Section 8.5 (Pets): Homeowners are permitted to keep up to two (2) domestic pets (dogs or cats). "
           "No individual pet may exceed a weight limit of 35 lbs. Commercial breeding is strictly prohibited."
    },
    "bylaws.txt": {
        0: "Article VI, Section 2: Pet regulations may be amended by the Board of Directors. "
           "The weight limit for dogs is set at 35 lbs, matching the restriction outlined in Section 8.5 of the CC&Rs."
    },
    "resale_cert.txt": {
        0: "Resale Certificate - Unit 204B:\n"
           "Current monthly assessment: $450.00.\n"
           "Pending special assessments: Yes, a pending $5,000 roofing assessment is noted.\n"
           "Active rental leasing status: The association lease cap of 15% is currently at 14.8% occupancy (Lease Cap limit near)."
    }
}

def read_mcp_document_chunk(file_path: str, chunk_id: int) -> dict:
    """Reads a chunk of extracted, PII-redacted text for the specified document.
    
    This tool simulates fetching raw aggregated text from the Supabase jobs table
    after conversion.

    Args:
        file_path: The name or path of the document (e.g. 'financials.txt', 'ccrs.txt').
        chunk_id: The specific text chunk index to retrieve (0-indexed).

    Returns:
        dict: A dictionary containing the 'text' of the chunk, or an error status.
    """
    doc_name = file_path.split("/")[-1]
    if doc_name not in MOCK_DOCUMENTS:
        return {
            "status": "error",
            "message": f"Document '{doc_name}' not found in Supabase job extracted_text."
        }
    
    chunks = MOCK_DOCUMENTS[doc_name]
    if chunk_id not in chunks:
        return {
            "status": "error",
            "message": f"Chunk ID {chunk_id} not found. Document has {len(chunks)} chunks."
        }
        
    return {
        "status": "success",
        "file_name": doc_name,
        "chunk_id": chunk_id,
        "text": chunks[chunk_id]
    }

def validate_cross_reference(category_id: str) -> dict:
    """Validates structural cross-reference constraints (XR-1 through XR-6) for a given category.

    Args:
        category_id: The cross-reference rule category (e.g., 'XR-1', 'XR-2', 'XR-5').

    Returns:
        dict: Validation results containing 'status', 'matched', and any 'discrepancies'.
    """
    valid_categories = ["XR-1", "XR-2", "XR-3", "XR-4", "XR-5", "XR-6"]
    if category_id not in valid_categories:
        return {
            "status": "error",
            "message": f"Invalid cross-reference category '{category_id}'. Valid rules are XR-1 through XR-6."
        }
        
    # Simulated validation logic for the mock documents
    validation_map = {
        "XR-1": {
            "matched": True,
            "rule": "Financial Liabilities to CC&R Sections",
            "discrepancies": []
        },
        "XR-2": {
            "matched": True,
            "rule": "Resale Certificate to Bylaws Constraints",
            "discrepancies": []
        },
        "XR-3": {
            "matched": True,
            "rule": "Monthly HOA Dues to Current Year Budget Dues",
            "discrepancies": []
        },
        "XR-4": {
            "matched": False,
            "rule": "Reserve Study Underfunding to Maintenance Schedule",
            "discrepancies": [
                "Reserve study recommends $400,000 but current reserve is $120,000. Underfunded by $280,000 (30% funded)."
            ]
        },
        "XR-5": {
            "matched": False,
            "rule": "Pending assessment vs Special Assessment rules in CC&Rs",
            "discrepancies": [
                "CC&R Section 4.2 requires member vote for special assessments exceeding $1,000 per unit. "
                "Pending roofing assessment is $5,000 per unit, which exceeds $1,000 limit and requires vote verification."
            ]
        },
        "XR-6": {
            "matched": True,
            "rule": "Risk findings map to source document and section",
            "discrepancies": []
        }
    }
    
    result = validation_map[category_id]
    return {
        "status": "success",
        "category_id": category_id,
        "rule_name": result["rule"],
        "is_valid": result["matched"],
        "discrepancies": result["discrepancies"]
    }
