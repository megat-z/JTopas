import os
import time
import json
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Define the Schema using Pydantic
class TestCaseAnalysis(BaseModel):
    test_id: str
    relevance: float
    complexity: float

def wait_for_files_active(client, files):
    """Waits for the uploaded files to be processed and ready for use."""
    print("Waiting for file processing...", end="")
    for file_obj in files:
        current_file = client.files.get(name=file_obj.name)
        while current_file.state == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            current_file = client.files.get(name=file_obj.name)
        
        if current_file.state != "ACTIVE":
            raise Exception(f"File {current_file.name} failed to process: {current_file.state}")
    print("Done")

def main():
    # 2. Configure Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    client = genai.Client(api_key=api_key)

    if not os.path.exists("dff.txt") or not os.path.exists("test_case.txt"):
        print("Error: Input files (dff.txt, test_case.txt) not found locally.")
        return

    # 3. Upload Files (FIXED: Use 'file=' instead of 'path=')
    print("Uploading files to Gemini...")
    diff_file = client.files.upload(file="dff.txt", config={'display_name': 'Git Diff'})
    test_file = client.files.upload(file="test_case.txt", config={'display_name': 'Test Cases'})

    wait_for_files_active(client, [diff_file, test_file])

    # 4. Generate Content
    prompt = "Analyze the attached Git Diff and Test Cases. Return a list containing an analysis for every test case found."

    print("Analyzing with gemini-2.5-pro...")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[diff_file, test_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[TestCaseAnalysis]
            )
        )

        # 5. Process Result
        if not response.parsed:
             raise ValueError("Model returned valid JSON but failed to parse into schema.")

        formatted_dict = {}
        for analysis in response.parsed:
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