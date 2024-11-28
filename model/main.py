import sys
import os
from flask import Flask, render_template, request, redirect
# Set the base directory to the parent directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the 'controller' directory to the Python path
sys.path.insert(0, os.path.join(base_dir, 'controller'))

# Import functions from control.py
from control import upload_document, blockchain

app = Flask(__name__, template_folder=os.path.join(base_dir, 'view', 'templates'), static_folder=os.path.join(base_dir, 'view', 'scripts'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'document' not in request.files:
            print("No document part in the request")
            return redirect(request.url)
        
        document = request.files['document']
        
        if document.filename == '':
            print("No selected file")
            return redirect(request.url)
        
        document_content = document.read()
        print("Received document:", document.filename)
        print("Document content (first 100 bytes):", document_content[:100])  # Print first 100 bytes for brevity
        document_hash = upload_document(document_content)
        print("Document hash:", document_hash)
        return render_template('upload_success.html', document_hash=document_hash)
    return render_template('upload.html')

@app.route('/blockchain_status')
def blockchain_status():
    blockchain_data = [
        {
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.hash
        }
        for block in blockchain.chain
    ]
    return render_template('blockchain_status.html', blockchain=blockchain_data)

if __name__ == '__main__':
    app.run(debug=True)