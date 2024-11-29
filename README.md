# Document Verification System

![Python badge](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask badge](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![HTML5 badge](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3 badge](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Jinja badge](https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white)

## Overview
This project provides a secure and reliable way to verify document authenticity using blockchain technology and AES-based digital signatures. The system is built using Python and Flask for the backend, along with HTML, CSS, and Jinja for the frontend.

## Features
- **Document Upload**: Upload documents to be hashed and stored in the blockchain.
- **Tampering Verification**: Verify if a document has been tampered with using its hash.
- **Digital Signatures**: Sign documents using AES-based digital signatures and store the signatures in the blockchain.
- **Signature Verification**: Verify the authenticity of a document's signature using AES keys.
- **Blockchain Status**: View the current status of the blockchain, including all blocks and their data.

## How It Works
1. **Document Upload**:
    - The document is hashed using SHA-256 and stored in the blockchain with its filename and a unique document ID.
    - A new block is created and added to the blockchain.

2. **Tampering Verification**:
    - Users can upload a document and provide its document ID.
    - The system computes the document's hash and verifies it against the stored hash in the blockchain.
    - Verification results indicate whether the document is valid, tampered, or not found.

3. **Digital Signatures**:
    - Users can sign a document using an AES key.
    - The document's hash is encrypted using the AES key, creating a digital signature.
    - The signature and document hash are stored in the blockchain, with "SIGNATURE" appended to the filename.

4. **Signature Verification**:
    - Users provide the signed document and the AES key.
    - The system verifies the signature by decrypting the stored signature and comparing it with the computed document hash.
    - Successful verification confirms the document's authenticity.

5. **Blockchain Status**:
    - Users can view the current status of the blockchain, including all blocks, their indexes, timestamps, and data.

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
Access the Application: Open your web browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Features:
- **Sign Documents**: Navigate to the "Sign" page, upload a document, and receive an AES key and signed document.
- **Verify Signatures**: Navigate to the "Verify Signature" page, upload the signed document, and provide the AES key.
- **Upload Documents**: Navigate to the "Upload" page to upload documents to the blockchain.
- **Verify Documents**: Navigate to the "Verify" page to check document tampering.
- **View Blockchain Status**: Navigate to the "Blockchain Status" page to see all blockchain entries.