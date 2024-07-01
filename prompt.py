import os
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

# Configuration section
GOOGLE_APPLICATION_CREDENTIALS_PATH = "C:/Users/User/Music/learn/bilvantis-learning-portal-backend-e_learning_pre_prod/AI_Modle/service.json"
PROJECT_ID = "fast-cascade-369003"
LOCATION = "us-central1"
MODEL_NAME = "gemini-1.5-flash-001"
MAX_OUTPUT_TOKENS = 8192
TEMPERATURE = 1
TOP_P = 0.95
DIRECTORY_PATH = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/"
OUTPUT_FILE_TXT = "Ai_output.txt"
OUTPUT_FILE_HTML = "Ai_output.html"

# Initialize Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH

# Function to read the content of the Python file
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to generate content using Vertex AI
def generate_content_for_review(code_content):
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    model = GenerativeModel(MODEL_NAME)

    generation_config = {
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    prompt = f""" Syntax Errors: Analyze the provided Python code snippet and identify syntax errors lines only. Explanation: identified each errors, here provide a clear and concise explanation of the issue. Fix:  And for that identified errors, Suggest a specific fix and provide only the necessary code and Do not write the entire code'
                  Code Improvement Suggestion: To improve the code, provide suggestions and write the necessary points only. Do not write the entire code. If No Code Improve Suggestions are found, simply state 'No Code Improve Suggestions Found'
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

# Function to read the output file
def read_output_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

# Function to convert output lines to HTML format
def convert_to_html(output_lines):
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                background-color: #f0f0f0;
                padding: 20px;
            }
            .file-section {
                margin-bottom: 10px;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #fff;
            }
            .syntax-errors {
                color: #FF5733; /* Orange-red */
            }
            .code-improvement {
                color: #3498DB; /* Blue */
            }
            .error-line {
                color: #FF5733; /* Orange-red */
                font-weight: bold;
            }
            .fix-code {
                background-color: #f9f9f9;
                padding: 5px;
                border-left: 3px solid #4CAF50; /* Green */
                margin-left: 10px;
            }
            .improvement-suggestion {
                background-color: #f9f9f9;
                padding: 5px;
                border-left: 3px solid #3498DB; /* Blue */
                margin-left: 10px;
            }
            pre, code {
                background-color: #f0f0f0;
                padding: 5px;
                border-radius: 3px;
            }
            h2, h3, p {
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
    '''

    current_section = None

    for line in output_lines:
        line = line.strip()
        if line.startswith("Reviewing file:"):
            if current_section:
                html_content += '</div>\n'
            html_content += f'<div class="file-section"><h2>{line}</h2>\n'
        elif line.startswith("## Syntax Errors:"):
            current_section = "syntax-errors"
            html_content += f'<div class="{current_section}"><h3>{line}</h3>\n'
        elif line.startswith("## Code Improvement Suggestions:"):
            current_section = "code-improvement"
            html_content += f'<div class="{current_section}"><h3>{line}</h3>\n'
        elif line.startswith("**") and current_section:
            html_content += f'<p class="error-line">{line}</p>\n'
        elif line.startswith("```python"):
            html_content += '<pre><code>\n'
        elif line.startswith("```"):
            html_content += '</code></pre>\n'
        elif line.strip() == "":
            html_content += '<br>\n'
        else:
            html_content += f'<p>{line}</p>\n'

    if current_section:
        html_content += '</div>\n'

    html_content += '''
    </body>
    </html>
    '''

    return html_content

# Function to write HTML content to a file
def write_html_file(html_content, output_file):
    with open(output_file, 'w') as file:
        file.write(html_content)

# Main function
def main():
    with open(OUTPUT_FILE_TXT, 'w') as f:
        python_files = [os.path.join(DIRECTORY_PATH, file) for file in os.listdir(DIRECTORY_PATH) if file.endswith('.py')]

        for file_path in python_files:
            code_content = read_file_content(file_path)
            f.write(f"\n\nReviewing file: {file_path}\n")
            response_text = generate_content_for_review(code_content)
            if response_text.strip():
                f.write(response_text + "\n")
            else:
                f.write("No response received from the AI model.\n")

    output_lines = read_output_file(OUTPUT_FILE_TXT)
    html_content = convert_to_html(output_lines)
    write_html_file(html_content, OUTPUT_FILE_HTML)
    print(f"HTML file '{OUTPUT_FILE_HTML}' has been generated successfully.")

if __name__ == "__main__":
    main()
