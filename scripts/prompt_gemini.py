import os
import json
import google.generativeai as genai

def get_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def main():
    # Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Load Context
    diff_content = get_file_content("dff.txt")
    test_cases_content = get_file_content("test_case.txt") # Expected list of test names
    
    # detailed prompt to enforce JSON structure
    prompt = f"""
    You are a specialized Software Engineering Assistant for Test Case Prioritization.
    
    Task: Analyze the following Code Changes (Git Diff) and assess the relevance of the provided Test Cases.
    
    CONTEXT:
    
    --- BEGIN GIT DIFF ---
    {diff_content}
    --- END GIT DIFF ---
    
    --- BEGIN TEST CASES ---
    {test_cases_content}
    --- END TEST CASES ---
    
    INSTRUCTIONS:
    1. Analyze the semantic intent of the code changes.
    2. For EACH test case listed, determine:
       - "relevance": A float between 0.0 (irrelevant) and 1.0 (critical).
       - "complexity": A float between 0.0 (trivial) and 1.0 (highly complex logic).
       - "change_nature": A short string describing the type of change (e.g., "refactor_tokenizer", "bugfix_parsing", "ui_update").
    3. OUTPUT format must be strictly a JSON object. Do not include markdown formatting.
    
    Example Output format:
    {{
        "TestTokenizerProperties": {{ "relevance": 0.8, "complexity": 0.5, "change_nature": "logic_change" }},
        "TestDifficultSituations": {{ "relevance": 0.2, "complexity": 0.9, "change_nature": "none" }}
    }}
    """
    
    # Call Gemini
    model = genai.GenerativeModel('gemini-3-pro-preview')
    response = model.generate_content(prompt)
    
    # valid response handling
    try:
        # Strip markdown code blocks if present
        clean_response = response.text.replace('```json', '').replace('```', '').strip()
        # Validate JSON
        json_data = json.loads(clean_response)
        
        # Save to llm.txt (acting as a JSON file)
        with open("llm.txt", "w") as f:
            json.dump(json_data, f, indent=4)
            
        print("Successfully generated llm.txt")
        
    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        # Fallback: write raw text for manual debugging if needed, though this breaks the pipeline
        with open("llm.txt", "w") as f:
            f.write(clean_response)

if __name__ == "__main__":
    main()