import os
import time
import json
import typing_extensions as typing
import google.generativeai as genai

def wait_for_files_active(files):
    """Waits for the uploaded files to be processed and ready for use."""
    print("Waiting for file processing...", end="")
    for name in (f.name for f in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("Done")

# Define the schema for the individual test analysis
class TestAnalysis(typing.TypedDict):
    relevance: float
    complexity: float

def main():
    # 1. Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    # 2. Upload Files (File API)
    # This uploads the files to Google's servers, allowing the model to reference them directly.
    if not os.path.exists("dff.txt") or not os.path.exists("test_case.txt"):
        print("Error: Input files (dff.txt, test_case.txt) not found locally.")
        return

    print("Uploading files to Gemini...")
    diff_file = genai.upload_file(path="dff.txt", mime_type="text/plain", display_name="Git Diff")
    test_file = genai.upload_file(path="test_case.txt", mime_type="text/plain", display_name="Test Cases")

    # Wait for files to be 'ACTIVE'
    wait_for_files_active([diff_file, test_file])

    # 3. Initialize Model with 'gemini-2.5-pro'
    # We rely on the specific model name provided.
    model = genai.GenerativeModel('gemini-2.5-pro')

    # 4. Generate Content with Structured Output
    # We pass the file objects directly in the contents list.
    # response_schema enforces the dict[str, TestAnalysis] format.
    prompt = "Analyze the attached Git Diff and Test Cases. For every test case listed, determine its relevance and complexity."

    print("Analyzing with gemini-2.5-pro...")
    
    try:
        response = model.generate_content(
            contents=[diff_file, test_file, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=dict[str, TestAnalysis] 
            )
        )

        # 5. Process and Save Result
        # The response is strictly JSON.
        json_data = json.loads(response.text)
        
        with open("llm.txt", "w") as f:
            json.dump(json_data, f, indent=4)
            
        print("Successfully generated llm.txt")

    except Exception as e:
        print(f"An error occurred: {e}")
        # If the model name is invalid or the API key doesn't have access to 2.5 yet,
        # it will catch here.

if __name__ == "__main__":
    main()