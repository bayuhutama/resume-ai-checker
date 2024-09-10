# Backend (Python)
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
import anthropic

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_resume(file_path):
    # Extract text from PDF
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    # Analyze text using Claude API
    client = anthropic.Anthropic(api_key="insert-your-claude-api-key-here")
    
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze the following resume and provide insights:\n\n{text}"
                }
            ]
        )
        analysis = response.content[0].text
    except Exception as e:
        analysis = f"Error: Unable to analyze resume. {str(e)}"
    
    return analysis

# ... rest of the code ...

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return 'No file part'
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return 'No selected file'
        
        results = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                analysis = analyze_resume(file_path)
                results.append({'filename': filename, 'analysis': analysis})
                os.remove(file_path)
        
        return render_template('result.html', results=results)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
