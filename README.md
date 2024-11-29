# Document Verification System

![Python badge](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask badge](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![HTML5 badge](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3 badge](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Jinja badge](https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white)

## Overview
This project provides a secure and reliable way to verify document authenticity using blockchain technology and AES-based digital signatures. The system is built using Python and Flask for the backend, along with HTML, CSS, and Jinja for the frontend.

## Features 
- **Sign Documents**: Navigate to the "Sign" page, upload a document, and receive an AES key along with the signed document. The document’s hash is encrypted using the AES key to create a digital signature, which is then stored in the blockchain.
- **Verify Signatures**: Navigate to the "Verify Signature" page, upload the signed document, and provide the AES key. The system verifies the signature by decrypting the stored signature using the AES key and comparing it with the hash of the uploaded document.
- **Upload Documents**: Navigate to the "Upload" page to upload documents to the blockchain. The document is hashed using SHA-256, and the hash is stored in the blockchain along with the document’s filename and a unique document ID.
- **Verify Documents**: Navigate to the "Verify" page to check document tampering. Upload the document and provide its document ID. The system compares the document’s hash with the stored hash in the blockchain to verify its authenticity.
- **Encrypt Documents**: During the signing process, the document's hash is encrypted using AES encryption. This ensures the integrity and confidentiality of the signature.
- **Decrypt Documents**: During signature verification, the encrypted hash (signature) is decrypted using the provided AES key to verify the document’s integrity.
- **View Blockchain Status**: Navigate to the "Blockchain Status" page to see all blockchain entries. This includes the indexes, timestamps, filenames, document IDs, and the hash or signature data for each block.


## Installation
To install the required dependencies, run:
```sh
pip install -r requirements.txt
```

## Usage
Run the Flask App:
```sh
python main.py
```
## Access the Application
Open your web browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
