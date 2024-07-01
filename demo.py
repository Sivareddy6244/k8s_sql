import os
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

# Initialize Google Application Credentials
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/User/Music/learn/bilvantis-learning-portal-backend-e_learning_pre_prod/AI_Modle/service.json"


# Function to read the content of the Python file
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# Function to generate content using Vertex AI
def generate_content_for_review(code_content):
    vertexai.init(project="fast-cascade-369003", location="us-central1")

    model = GenerativeModel("gemini-1.5-flash-001")

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    prompt = f"""
Syntax Errors: Analyze the following Python code snippet and identify any syntax errors. If no syntax errors are found, simply state 'No syntax errors detected'.
Explanation: For each error, provide a clear and concise explanation of the issue.
Fix: Suggest a specific fix and provide only the necessary code.
Code Improvement Suggestion: To improve the code, provide suggestions and write the necessary points only. Do not write the entire code.

{code_content}
    """

    responses = model.generate_content(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    response_text = ""
    for response in responses:
        response_text += response.text

    return response_text


# Main function
def main():
    directory_path = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/"  # Replace with your directory path
    python_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.py')]

    for file_path in python_files:
        code_content = read_file_content(file_path)
        print(f"\n\nReviewing file: {file_path}")
        response_text = generate_content_for_review(code_content)
        if response_text.strip():
            print(response_text)
        else:
            print("No response received from the AI model.")


if __name__ == "__main__":
    main()
