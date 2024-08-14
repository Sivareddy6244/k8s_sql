import os
import subprocess
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models

# Set your Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service.json"

# Initialize Vertex AI with the project and location
vertexai.init(project="bilvantis-qa", location="us-central1")

# Define the generation config and safety settings globally
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

# Initialize the Generative Model
generative_model = GenerativeModel("gemini-1.5-flash-001")


def read_file_content(file_path):
    """Reads the content of the file."""
    with open(file_path, 'r') as file:
        return file.read()


def add_line_numbers(code_content):
    """Adds line numbers to code content for better error referencing."""
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)


def generate_content_for_review(code_content):
    """Generates a detailed review of the provided code snippet."""
    response_text = ""
    try:
        responses = generative_model.generate_content(
            [prompt(code_content)],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        for response in responses:
            response_text += response.text

    except ValueError as e:
        if "SAFETY" in str(e):
            print(f"WARNING: Generated content blocked by safety filters: {e}")
        else:
            raise e

    return response_text


def prompt(code_content):
    """Creates a prompt to analyze code for various issues."""
    return f"""Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors : **
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.

2. ** Code Bugs : **
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.

3. ** Security Vulnerabilities : **
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.

4. ** Duplicate Code : **
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.

5. ** Code Improvement Suggestions : **
    - ** Identification **: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - ** Suggestion **: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - ** Note **: If no code improvement suggestions are found, simply state "No Code Improvement Suggestions Found."
6. ** Don't write any kind of code or code snippet in the output: **
    - They shouldn't be any code in the output.

** The Code : **
{code_content}
"""


def process_changed_files(directory_path, output_file_path):
    """Processes each changed file in the directory and generates a review."""
    # Get the list of changed files
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^..HEAD'], capture_output=True, text=True)
    changed_files = result.stdout.splitlines()

    # Filter changed files that are in the specified directory
    code_files = [file for file in changed_files if file.startswith(directory_path)]

    with open(output_file_path, 'w') as output_file:
        for file_path in code_files:
            if os.path.isfile(file_path):
                code_content = read_file_content(file_path)
                code_content_with_line_numbers = add_line_numbers(code_content)
                print(f"\n\nReviewing file: {file_path}")
                response_text = generate_content_for_review(code_content_with_line_numbers)
                if response_text.strip():
                    output_file.write(f"\n\nReview for file: {file_path}\n")
                    output_file.write(response_text)
                else:
                    output_file.write(f"\n\nReview for file: {file_path}\n")
                    output_file.write("No response received from the AI model.")
            else:
                print(f"{file_path} does not exist or was renamed. Skipping...")


def prompt_for_comparison(old_content, new_content):
    """Creates a prompt to instruct the AI model to compare the old and new content."""
    return f"""carefully read two sets of code review responses. The first set is the old response file, and the second set is the new response file. Your task is to read and compare these responses files and identify any latest, unique points or comments present in the new response that are not in the old response and ignore common related things.

### Old Response:
{old_content}

### New Response:
{new_content}

### Instructions:
1. **Identify Unique Issues:** Highlight only the issues or comments that appear in the new response but not in the old response.
2. **Avoid Repetitions:** If any points from the old response are repeated or similarly phrased in the new response, ignore them.
3. **Format:** Present each unique issue clearly and concisely.
4. **Separation:** Ensure each unique issue is separated by a double newline for readability.
5. **common points:** ignore, if you find any common points in both response files.

### Output:
For each unique issue, provide a detailed analysis in the following format:

Review for file: [file path]
## Code Analysis:

### 1. Syntax Errors:

- **Identification:** [Line number and error description]
- **Explanation:** [Explanation of the syntax error]
- **Fix:** [Suggested fix for the error]

### 2. Code Bugs:

- **Identification:** [Line number and bug description]
- **Explanation:** [Explanation of the bug]
- **Fix:** [Suggested fix for the bug]

### 3. Security Vulnerabilities:

- **Identification:** [Line number and vulnerability description]
- **Explanation:** [Explanation of the vulnerability]
- **Fix:** [Suggested fix for the vulnerability]

### 4. Duplicate Code:

- **Identification:** [Line number and description of duplicate code]
- **Suggestion:** [Suggested changes to avoid duplication]

### 5. Code Improvement Suggestions:

- **Identification:** [Line number and description of improvement area]
- **Suggestion:** [Suggested improvement]

### 6. No code in the output:

- Ensure that no code snippets are included in the analysis.
"""


def generate_unique_issues_report(old_file_path, new_file_path, output_file_path):
    """Generates a report of unique issues from the new response compared to the old response."""
    # Read the contents of both files
    old_content = read_file_content(old_file_path)
    new_content = read_file_content(new_file_path)

    # Create the prompt for comparison
    comparison_prompt = prompt_for_comparison(old_content, new_content)

    # Generate the response using the same Generative Model
    try:
        responses = generative_model.generate_content(
            [comparison_prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        unique_issues = ""
        for response in responses:
            unique_issues += response.text

    except Exception as e:
        print(f"Error generating unique issues report: {e}")
        unique_issues = "Error generating report. Please check the AI model and input data."

    # Write the unique issues to the output file
    with open(output_file_path, 'w') as output_file:
        output_file.write(unique_issues)


def main():
    # Directory path
    python_dir = "code/dataform/"
    # Output file paths
    python_response_file = "current_python_response.txt"

    # Process changed files to generate reviews
    process_changed_files(python_dir, python_response_file)

    # File paths for old and new response files
    old_python_response_file = "code/dataform/old_python_response.txt"
    new_python_response_file =  python_response_file
    final_output_file = "final_python_response.txt"

    # Compare old and new responses to generate unique issues report
    generate_unique_issues_report(old_python_response_file, new_python_response_file, final_output_file)


if __name__ == "__main__":
    main()

