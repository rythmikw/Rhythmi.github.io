# app/process.py
from flask import Flask, render_template, request, jsonify, send_file
from model import process_ecg_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Save the file to a temporary location
        file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        file.save(file_path.name)

        # Process the file
        output = process_ecg_file(file_path.name)

        # Delete the temporary file
        os.remove(file_path.name)

        return jsonify(output)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download/<filename>')
def download(filename):
    try:
        # Send the PDF file for download
        return send_file(f'app/static/{filename}', as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
