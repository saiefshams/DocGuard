import sys
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
from io import BytesIO
from tempfile import NamedTemporaryFile
import hashlib

# Set the base directory to the parent directory
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the 'controller' directory to the Python path
sys.path.insert(0, os.path.join(base_dir, 'controller'))

# Import functions from control.py
from control import upload_document, blockchain, generate_aes_key, encrypt_document, decrypt_document, verify_document, sign_document, verify_document_signature

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
        filename = document.filename
        print("Received document:", filename)
        print("Document content (first 100 bytes):", document_content[:100])  # Print first 100 bytes for brevity
        document_hash, document_id = upload_document(document_content, filename)
        print("Document hash:", document_hash)
        return render_template('upload_success.html', document_hash=(document_hash, document_id))
    return render_template('upload.html')

@app.route('/blockchain_status')
def blockchain_status():
    blockchain_data = [
        {
            'index': block.index,
            'timestamp': block.timestamp_str,
            'data': block.data if block.index == 0 else block.data,  # Handle data without eval()
        }
        for block in blockchain.chain
    ]
    return render_template('blockchain_status.html', blockchain=blockchain_data)

@app.route('/detailed_blockchain_status')
def detailed_blockchain_status():
    blockchain_data = [
        {
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp_str,  # Ensure this uses timestamp_str
            'data': block.data if block.index == 0 else block.data,  # Handle data without eval()
            'hash': block.hash
        }
        for block in blockchain.chain
    ]
    return render_template('detailed_blockchain_status.html', blockchain=blockchain_data)

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

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    result = None
    if request.method == 'POST':
        if 'document' not in request.files:
            print("No document part in the request")
            return redirect(request.url)
        
        document = request.files['document']
        
        if document.filename == '':
            print("No selected file")
            return redirect(request.url)
        
        document_content = document.read()
        filename = document.filename
        result = verify_document(document_content, filename)
    
    return render_template('verify.html', result=result)

@app.route('/sign_verify')
def sign_verify():
    return render_template('sign_verify.html')

@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        file = request.files['file']

        # Read file content
        file_content = file.read()

        # Generate AES key for signing
        aes_key = generate_aes_key()

        # Sign the document with AES
        signature = sign_document(file_content, aes_key)

        # Append "SIGNATURE" to the filename
        signature_filename = f"{file.filename}_SIGNATURE"

        # Store the signature and document hash in the blockchain
        blockchain.add_block({
            'type': 'signature',
            'filename': signature_filename,
            'signature': signature,
            'document_hash': signature['document_hash']
        })

        # Render the signature result template with AES key
        return render_template('signature_result.html', aes_key=aes_key)

    return render_template('sign.html')

@app.route('/verify_signature', methods=['GET', 'POST'])
def verify_signature():
    if request.method == 'POST':
        file = request.files['file']
        aes_key = request.form['key']  # Read AES key from form

        # Read file content
        file_content = file.read()

        # Construct expected signature filename
        signature_filename = f"{file.filename}_SIGNATURE"

        # Verify if the signature exists in the blockchain
        for block in blockchain.chain:
            if block.index == 0:
                continue
            if block.data.get('type') == 'signature' and block.data.get('filename') == signature_filename:
                signature = block.data.get('signature')
                if not signature:
                    continue
                # Use the provided AES key for verification
                if verify_document_signature(file_content, aes_key, signature):
                    return render_template('verification_successful.html')

        flash('Signature verification failed!', 'danger')
        return redirect(url_for('sign_verify'))

    return render_template('verify_signature.html')


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