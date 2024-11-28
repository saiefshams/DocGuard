from flask import Flask, render_template

app = Flask(__name__, template_folder='../view/templates', static_folder='../view/scripts')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


'''#########################
#Interface of application#

from flask import Flask, request, render_template
import hashlib

app = Flask(__name__)
document_hashes = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    document = request.files['document']
    document_content = document.read()
    document_hash = hashlib.sha256(document_content).hexdigest()
    document_hashes[document_hash] = True
    return 'Document uploaded and hash stored.'

@app.route('/verify', methods=['POST'])
def verify_document():
    document = request.files['document']
    document_content = document.read()
    document_hash = hashlib.sha256(document_content).hexdigest()
    if document_hashes.get(document_hash):
        return 'Document is verified.'
    else:
        return 'Document verification failed.'

if __name__ == '__main__':
    app.run(debug=True)

    
###############################
#Interface of application#

<!DOCTYPE html>
<html>
<head>
    <title>Document Verification System</title>
</head>
<body>
    <h1>Upload Document</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="document">
        <input type="submit" value="Upload">
    </form>

    <h1>Verify Document</h1>
    <form action="/verify" method="post" enctype="multipart/form-data">
        <input type="file" name="document">
        <input type="submit" value="Verify">
    </form>
</body>
</html>
'''