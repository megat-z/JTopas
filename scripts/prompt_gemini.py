import os
import time
import json
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Define the Schema using Pydantic (New SDK Standard)
class TestCaseAnalysis(BaseModel):
    test_id: str
    relevance: float
    complexity: float

def wait_for_files_active(client, files):
    """Waits for the uploaded files to be processed and ready for use."""
    print("Waiting for file processing...", end="")
    for file_obj in files:
        # The new SDK uses client.files.get() to refresh metadata
        current_file = client.files.get(name=file_obj.name)
        while current_file.state == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            current_file = client.files.get(name=file_obj.name)
        
        if current_file.state != "ACTIVE":
            raise Exception(f"File {current_file.name} failed to process: {current_file.state}")
    print("Done")

def main():
    # 2. Configure Client (New 'Client' pattern)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # The new SDK initializes a client instance rather than global configuration
    client = genai.Client(api_key=api_key)

    if not os.path.exists("dff.txt") or not os.path.exists("test_case.txt"):
        print("Error: Input files (dff.txt, test_case.txt) not found locally.")
        return

    # 3. Upload Files (Updated Method)
    print("Uploading files to Gemini...")
    # 'path' is used instead of 'path' arg, but key concept is client.files.upload
    diff_file = client.files.upload(path="dff.txt", config={'display_name': 'Git Diff'})
    test_file = client.files.upload(path="test_case.txt", config={'display_name': 'Test Cases'})

    wait_for_files_active(client, [diff_file, test_file])

    # 4. Generate Content with Structured Output
    prompt = "Analyze the attached Git Diff and Test Cases. Return a list containing an analysis for every test case found."

    print("Analyzing with gemini-2.5-pro...")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[diff_file, test_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                # The new SDK accepts the Python class/list directly
                response_schema=list[TestCaseAnalysis]
            )
        )

        # 5. Process Result (New 'parsed' attribute)
        # The new SDK automatically parses the JSON into Pydantic objects for you
        if not response.parsed:
             raise ValueError("Model returned valid JSON but failed to parse into schema.")

        # Convert the list of Pydantic objects back to your specific Dict format
        # Expected Output: { "TC001": { "relevance": 0.9, "complexity": 0.5 }, ... }
        formatted_dict = {}
        for analysis in response.parsed:
            # .model_dump() converts Pydantic object to dict
            item_data = analysis.model_dump()
            t_id = item_data.pop("test_id")
            formatted_dict[t_id] = item_data

        with open("llm.txt", "w") as f:
            json.dump(formatted_dict, f, indent=4)
            
        print(f"Successfully generated llm.txt with {len(formatted_dict)} entries.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()