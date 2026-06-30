# test_agent.py
import sys
import os
import json

# Add project root to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent import HOAAuditorLivePipeline
from app.supabase_client import get_supabase_client

def run_test():
    print("Initializing pipeline...")
    pipeline = HOAAuditorLivePipeline()
    pipeline.model_name = "gemini-3.5-flash"
    
    print("\n--- DATABASE SCHEMA CHECK ---")
    client = get_supabase_client()
    if client:
        # Check columns of hoa_reports
        try:
            res = client.table("hoa_reports").select("document_hash").limit(1).execute()
            print("✅ 'hoa_reports' has a top-level 'document_hash' column!")
        except Exception as e:
            print(f"❌ 'hoa_reports' does NOT have a top-level 'document_hash' column. Error: {e}")

        # Check columns of analysis_cache
        try:
            res = client.table("analysis_cache").select("document_hash").limit(1).execute()
            print("✅ 'analysis_cache' has a top-level 'document_hash' column!")
        except Exception as e:
            print(f"❌ 'analysis_cache' does NOT have a top-level 'document_hash' column. Error: {e}")
    else:
        print("Could not initialize Supabase client.")

    print(f"\nRunning agent analysis using model: {pipeline.model_name}...")
    try:
        report, was_cached = pipeline.run_agent_analysis()
        print("\n--- RUN COMPLETE ---")
        print(f"Was Cached: {was_cached}")
        print("\nResult payload keys:", list(report.keys()) if isinstance(report, dict) else type(report))
        if "error" in report:
            print(f"Error in report: {report['error']}")
        else:
            print("Successfully generated and parsed JSON report!")
    except Exception as e:
        print(f"\nExecution failed with error: {e}")

if __name__ == "__main__":
    run_test()
