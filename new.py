import os
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold

# Initialize Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/User/Music/learn/bilvantis-learning-portal-backend-e_learning_pre_prod/AI_Modle/service.json"


# Function to read the content of a Python file
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# Function to generate content using Vertex AI
def generate_content_for_review(code_content):
    from vertexai import init

    init(project="fast-cascade-369003", location="us-central1")

    model = GenerativeModel("gemini-1.5-flash-001")

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.5,
        "top_p": 0.95,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    prompt = (
        "Analyze the following Python code snippet and identify any syntax errors. "
        "For each error, provide a clear and concise explanation of the issue and suggest a specific fix. "
        "If no syntax errors are found, simply state 'No syntax errors detected':\n\n"
        f"{code_content}"
    )

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


# Function to generate HTML report
def generate_html_report(file_reviews):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .file-review {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .file-review h2 {
                margin-top: 0;
                color: #333;
            }
            .syntax-error, .no-errors {
                background-color: #f9f9f9;
                padding: 10px;
                border-left: 5px solid #d9534f;
                margin-bottom: 10px;
            }
            .no-errors {
                border-left-color: #5cb85c;
            }
            .syntax-error h3, .no-errors h3 {
                margin-top: 0;
                color: #d9534f;
            }
            .no-errors h3 {
                color: #5cb85c;
            }
            .explanation-heading {
                color: #5bc0de;  /* Light blue color for the Explanation heading */
            }
            .fix-heading {
                color: #337ab7;  /* Blue color for the Fix heading */
            }
            pre {
                background-color: #f7f7f7;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
            }
        </style>
        <title>Code Review Report</title>
    </head>
    <body>
    """

    for file_review in file_reviews:
        html_content += f"""
        <div class="file-review">
            <h2>Reviewing file: {file_review['file_path']}</h2>
        """
        review = file_review['review']

        if "No syntax errors detected" in review:
            html_content += """
            <div class="no-errors">
                <h3>No syntax errors detected.</h3>
            </div>
            """
        else:
            error_part = ""
            explanation_part = ""
            fix_part = ""
            result_part = ""

            if "**Error:**" in review:
                error_split = review.split('**Error:** ')
                error_part = error_split[1].split('**Explanation:**')[0].strip() if len(error_split) > 1 else ""
            if "**Explanation:**" in review:
                explanation_split = review.split('**Explanation:** ')
                explanation_part = explanation_split[1].split('**Fix:**')[0].strip() if len(explanation_split) > 1 else ""
            if "**Fix:**" in review:
                fix_split = review.split('**Fix:** ')
                fix_part = fix_split[1].split('**Result:**')[0].strip() if len(fix_split) > 1 else ""
            if "**Result:**" in review:
                result_split = review.split('**Result:** ')
                result_part = result_split[1].strip() if len(result_split) > 1 else ""

            html_content += f"""
            <div class="syntax-error">
                <h3>Syntax Error:</h3>
                <p>{error_part}</p>
            </div>
            <div>
                <h4 class="explanation-heading">Explanation:</h4>
                <p>{explanation_part}</p>
            </div>
            <div>
                <h4 class="fix-heading">Fix:</h4>
                <p>{fix_part}</p>
                <pre><code>{review.split('```python')[1].split('```')[0].strip() if '```python' in review else ''}</code></pre>
                <p>{result_part}</p>
            </div>
            """
        html_content += "</div>"

    html_content += """
    <p>Process finished with exit code 0.</p>
    </body>
    </html>
    """

    return html_content


# Main function
def main():
    directory_path = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/"  # Replace with your directory path
    python_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.py')]

    file_reviews = []

    for file_path in python_files:
        code_content = read_file_content(file_path)
        print(f"\n\nReviewing file: {file_path}")
        review = generate_content_for_review(code_content)
        file_reviews.append({
            "file_path": file_path,
            "review": review
        })

    html_report = generate_html_report(file_reviews)

    with open("code_review_report.html", "w") as file:
        file.write(html_report)

    print("HTML report generated: code_review_report.html")


if __name__ == "__main__":
    main()
