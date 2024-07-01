import pandas as pd

# Path to the uploaded file
file_path = 'ai_review_output.txt'

# Reading the text file
with open(file_path, 'r') as file:
    content = file.readlines()
    
# Define the fixed column widths (these values are approximate based on the observed data)
column_widths = [70, 50, 50]

# Function to parse a line based on the fixed column widths
def parse_line(line, widths):
    fields = []
    start = 0
    for width in widths:
        end = start + width
        fields.append(line[start:end].strip())
        start = end
    return fields

# Parse the file content
parsed_data = [parse_line(line, column_widths) for line in content[3:]]

# Define the headers
headers = ['File Name', 'Syntax Errors', 'Suggestions']

# Create the DataFrame
df = pd.DataFrame(parsed_data, columns=headers)

# Path to save the Excel file
excel_file_path = 'ai_review_output.xlsx'

# Saving to Excel
df.to_excel(excel_file_path, index=False)

# Return the path to the saved Excel file
excel_file_path
