import sys
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for
from io import BytesIO
from tempfile import NamedTemporaryFile

# Set the base directory to the parent directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the 'controller' directory to the Python path
sys.path.insert(0, os.path.join(base_dir, 'controller'))

# Import functions from control.py
from control import upload_document, blockchain, generate_aes_key, encrypt_document, decrypt_document

app = Flask(__name__, template_folder=os.path.join(base_dir, 'view', 'templates'), static_folder=os.path.join(base_dir, 'view', 'scripts'))
app.secret_key = os.urandom(24)

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

@app.route('/choose_encryption')
def choose_encryption():
    return render_template('choose_encryption.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        if 'document' not in request.files:
            print("No document part in the request")
            return redirect(request.url)
        
        document = request.files['document']
        
        if document.filename == '':
            print("No selected file")
            return redirect(request.url)
        
        original_filename = document.filename
        document_content = document.read()
        aes_key = generate_aes_key()
        nonce, ciphertext, tag = encrypt_document(document_content, aes_key)
        
        encrypted_content = {
            'nonce': nonce,
            'ciphertext': ciphertext,
            'tag': tag,
            'original_filename': original_filename
        }
        encrypted_content_bytes = str(encrypted_content).encode('utf-8')
        
        # Save the encrypted content to a temporary file and store the path in the session
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(encrypted_content_bytes)
            session['encrypted_file_path'] = temp_file.name
        
        session['aes_key'] = aes_key
        
        return render_template('encryption_result.html', aes_key=aes_key)
    
    return render_template('encrypt.html')

@app.route('/download_encrypted_file')
def download_encrypted_file():
    encrypted_file_path = session.get('encrypted_file_path')
    if encrypted_file_path:
        return send_file(encrypted_file_path, download_name='encrypted_document.enc', as_attachment=True)
    return redirect(url_for('choose_encryption'))

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        if 'document' not in request.files or 'key' not in request.form:
            print("No document or key part in the request")
            return redirect(request.url)
        
        document = request.files['document']
        aes_key = request.form['key']
        
        encrypted_content = document.read().decode('utf-8')
        encrypted_content = eval(encrypted_content)  # Convert back to dict
        
        nonce = encrypted_content['nonce']
        ciphertext = encrypted_content['ciphertext']
        tag = encrypted_content['tag']
        original_filename = encrypted_content['original_filename']
        
        try:
            document_content = decrypt_document(nonce, ciphertext, tag, aes_key)
            return send_file(BytesIO(document_content), download_name=original_filename, as_attachment=True)
        except ValueError:
            return "Invalid decryption key or corrupted file"
    
    return render_template('decrypt.html')



# error handling
@app.errorhandler(400)
def bad_request(error):
    return render_template('error.html', error_code=400, error_message='Bad Request: The server could not understand the request due to invalid syntax.'), 400

@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html', error_code=403, error_message='Forbidden: You do not have the necessary permissions to access this resource.'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_code=404, error_message='Page Not Found: The requested resource could not be found on this server.'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error_code=500, error_message='Internal Server Error: The server encountered an unexpected condition which prevented it from fulfilling the request.'), 500


if __name__ == '__main__':
    app.run(debug=True)