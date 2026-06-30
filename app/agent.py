# app/agent.py
import os
import json
import hashlib
import time
from google import genai
from google.genai import types
from app.schema import HOAAuditReport

def sanitize_json_newlines(json_str: str) -> str:
    """
    State-machine parser that scans raw response text.
    If it detects literal, physical line breaks inside active JSON string quotes,
    it converts them to safe escaped string literals (\\n) before decoding.
    """
    result = []
    in_string = False
    escaped = False
    for char in json_str:
        if char == '"' and not escaped:
            in_string = not in_string
        
        if char == '\\' and not escaped:
            escaped = True
        else:
            escaped = False
            
        if in_string and char in ('\n', '\r'):
            result.append('\\n')
        else:
            result.append(char)
    return "".join(result)

def escape_unescaped_quotes_in_json(json_str: str) -> str:
    """
    Scans a flattened JSON string line-by-line and escapes any raw,
    unescaped double quotes found inside string property values.
    """
    import re
    lines = json_str.splitlines()
    for i, line in enumerate(lines):
        match = re.match(r'^(\s*"[a-zA-Z0-9_-]+"\s*:\s*")(.*)("\s*,?\s*)$', line)
        if match:
            prefix, value, suffix = match.groups()
            escaped_value = []
            escaped = False
            for char in value:
                if char == '\\':
                    escaped = not escaped
                    escaped_value.append(char)
                elif char == '"':
                    if not escaped:
                        escaped_value.append('\\"')
                    else:
                        escaped_value.append(char)
                    escaped = False
                else:
                    escaped = False
                    escaped_value.append(char)
            lines[i] = prefix + "".join(escaped_value) + suffix
    return "\n".join(lines)

class HOAAuditorLivePipeline:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    clean_line = line.strip()
                    if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
                        continue
                    key, val = clean_line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: GEMINI_API_KEY missing from app/.env")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        
        # Explicitly using the gemini-3.5-flash model
        self.model_name = "gemini-3.5-flash"

    def run_agent_analysis(self) -> tuple[dict, bool]:
        """
        Token-Saving Agent Flow: Hashes document inventory text.
        Applies safe truncation, checks Supabase cache, and executes with 
        silent exponential retries to handle transient API demand spikes.
        """
        # 1. Ingest all target workspace text files dynamically
        combined_package_text = ""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mock_data')
        
        if os.path.exists(data_dir):
            for filename in sorted(os.listdir(data_dir)):
                if filename.endswith(".txt"):
                    file_path = os.path.join(data_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            snippet = content[:6000]  # Safe clipping budget
                            combined_package_text += f"\n\n=== FILE: {filename} ===\n{snippet}"
                    except Exception as e:
                        print(f"[INGESTION ERROR] {filename}: {e}")

        if not combined_package_text.strip():
            return {"error": "No source documents detected to audit."}, False

        # 2. GENERATE UNIQUE TEXT FINGERPRINT HASH
        doc_hash = hashlib.md5(combined_package_text.encode('utf-8')).hexdigest()

        # 3. INTERCEPT & CHECK SUPABASE FOR EXISTING RECORD
        try:
            from app.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                cached_query = supabase.table("hoa_reports").select("payload").eq("document_hash", doc_hash).execute()
                
                if cached_query.data:
                    print("🎯 [CACHE HIT] Identical document set detected! Retrieving directly from Supabase...")
                    cached_payload = cached_query.data[0]["payload"]
                    if isinstance(cached_payload, str):
                        return json.loads(cached_payload), True
                    return cached_payload, True
        except Exception as e:
            print(f"[CACHE CAUTION] Cache lookup bypassed: {e}")

        # 4. IF NOT CACHED: Load Manifest Rules and trigger live Gemini API Call
        manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'system', 'schemas', 'report_manifest.yaml')
        governance_rules = ""
        if os.path.exists(manifest_path):
            import yaml
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    governance_rules = yaml.dump(yaml.safe_load(f), default_flow_style=False)
            except Exception as e:
                print(f"[MANIFEST WARNING] Failed to read manifest: {e}")

        regulations_path = os.path.join(os.path.dirname(__file__), 'wucia_regulations.json')
        wucioa_framework = ""
        if os.path.exists(regulations_path):
            try:
                with open(regulations_path, 'r', encoding='utf-8') as f:
                    wucioa_framework = f.read()
            except Exception as e:
                print(f"[REGULATION WARNING] Failed to read checklist: {e}")

        governance_prompt = f"""
You are an expert real estate compliance risk system. Analyze the data and return a structured JSON object fitting the schema requirements perfectly.

CRITICAL GOVERNANCE MANIFEST CONSTRAINTS:
{governance_rules}

STATE COMPLIANCE MANDATE CHECKLIST (WASHINGTON STATE RCW 64.90.640):
{wucioa_framework}

SIMPLE ENGLISH TRANSLATION INSTRUCTION:
1. Identify and return ONLY the top 4 most critical financial or legal risks. Ignore minor issues.
2. The 'buyer_note' property MUST be a single short sentence explaining the direct out-of-pocket cost impact.
3. Cross-reference your findings by setting 'risk_id' to match the rules specified in the manifest (e.g. 'XR-1-1').
4. Include the exact citation anchors provided in the raw files using the formatting '[source: X]'.

HOA PACKAGE TEXT DATA TO AUDIT:
{combined_package_text}
"""

        if self.client:
            print(f"💸 [TOKEN EXPENSE] Triggering Native Pydantic {self.model_name} Call...")
            
            # Silent retry queue with exponential backoff: 1s, 2s, 4s, 8s, 16s
            backoff_delays = [1, 2, 4, 8, 16]
            response = None
            
            for attempt, delay in enumerate(backoff_delays):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=governance_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.1,
                            response_mime_type="application/json",
                            response_schema=HOAAuditReport,
                            max_output_tokens=8192,
                            thinking_config=types.ThinkingConfig(
                                thinking_budget=0
                            )
                        )
                    )
                    break  # Success, break retry loop
                except Exception as e:
                    if attempt == len(backoff_delays) - 1:
                        # All retries failed, return the error safely to prevent a dashboard crash
                        return {"error": f"Live generation failed after backoff retries: {e}"}, False
                    time.sleep(delay)  # Wait silently

            if response:
                try:
                    report_text = response.text.strip()
                    
                    # Write to a debug file in the workspace so we can inspect it
                    try:
                        debug_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_output.txt')
                        with open(debug_path, 'w', encoding='utf-8') as df:
                            df.write("--- RAW RESPONSE START ---\n")
                            df.write(report_text)
                            df.write("\n--- RAW RESPONSE END ---\n")
                            df.write("\n--- CANDIDATE METADATA ---\n")
                            if hasattr(response, 'candidates') and response.candidates:
                                candidate = response.candidates[0]
                                df.write(f"Finish Reason: {getattr(candidate, 'finish_reason', 'N/A')}\n")
                                df.write(f"Safety Ratings: {getattr(candidate, 'safety_ratings', 'N/A')}\n")
                    except Exception as de:
                        print(f"[DEBUG WRITE ERROR] {de}")
                    
                    # Clean physical string formatting splits
                    sanitized_text = sanitize_json_newlines(report_text)
                    
                    # Escape any unescaped quotes inside JSON string values
                    sanitized_text = escape_unescaped_quotes_in_json(sanitized_text)
                    
                    # Strict=False forces the decoder to handle raw control spaces cleanly
                    report_json = json.loads(sanitized_text, strict=False)
                    report_json["document_hash"] = doc_hash  
                    
                    return report_json, False
                except Exception as e:
                    return {"error": f"Failed to parse model structure: {e}"}, False
            else:
                return {"error": "No response returned from the model tier."}, False
        else:
            return {"error": "Simulation Mode: API key missing."}, False