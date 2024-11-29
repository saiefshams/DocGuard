import hashlib
import time
import pytz
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import uuid


# Blockchain classes
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        self.timestamp_str = self.format_timestamp()
        print(f"Block created - Index: {index}, Previous Hash: {previous_hash}, Timestamp: {timestamp}, Data: {data}, Hash: {hash}")

    def format_timestamp(self):
        # Format the timestamp to Canada time zone
        tz = pytz.timezone('Canada/Eastern')
        dt = datetime.fromtimestamp(self.timestamp, tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, data):
        return hashlib.sha256(f"{index}{previous_hash}{timestamp}{data}".encode()).hexdigest()

# Blockchain classes
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        print("Blockchain created with genesis block: ", self.chain)

    # Ensure the timestamp_str is correctly set in the Genesis block and new blocks
    def create_genesis_block(self):
        genesis_block = Block(0, "0", int(time.time()), "Genesis Block", Block.calculate_hash(0, "0", int(time.time()), "Genesis Block"))
        genesis_block.timestamp_str = genesis_block.format_timestamp()  # Ensure timestamp_str is set for the genesis block
        return genesis_block

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(latest_block.index + 1, latest_block.hash, int(time.time()), data, Block.calculate_hash(latest_block.index + 1, latest_block.hash, int(time.time()), data))
        new_block.timestamp_str = new_block.format_timestamp()  # Ensure timestamp_str is set for new blocks
        self.chain.append(new_block)
        print("New block added - Index: ", new_block.index, ", Hash: ", new_block.hash)
        return new_block

    def get_latest_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]  # Fixed typo here

            # Check if the current block's hash is correct
            if current_block.hash != Block.calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.data):
                print(f"Invalid block hash at index {current_block.index}")
                return False

            # Check if the current block's previous hash matches the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash at index {current_block.index}")
                return False

        print("Blockchain is valid")
        return True

# Initialize Blockchain
blockchain = Blockchain()

# Document hashing and upload functions
def hash_document(document):
    document_hash = hashlib.sha256(document).hexdigest()
    print("Calculated document hash:", document_hash)
    return document_hash

def upload_document(document_content, filename):
    document_hash = hash_document(document_content)
    document_id = str(uuid.uuid4())  # Generate a unique identifier for each document
    data = {'type': 'original', 'filename': filename, 'document_id': document_id, 'hash': document_hash}
    blockchain.add_block(data)
    print("Block added to blockchain. Current chain length:", len(blockchain.chain))
    return document_hash, document_id

def verify_document(document_content, filename, document_id):
    document_hash = hash_document(document_content)
    for block in blockchain.chain:
        if block.index == 0:
            continue
        block_data = block.data
        if block_data['filename'] == filename and block_data['document_id'] == document_id:
            if block_data['hash'] == document_hash:
                print("Document is valid and matches the blockchain record.")
                return {'status': 'valid', 'index': block.index, 'timestamp': block.timestamp_str, 'filename': filename, 'document_id': document_id, 'hash': block_data['hash']}
            else:
                print("Document content has been tampered.")
                return {'status': 'tampered', 'filename': filename}
    print("Document does not match any blockchain record.")
    return {'status': 'invalid'}


# AES Encryption and Decryption functions
def generate_aes_key():
    key = get_random_bytes(32) # 32 bytes = 256 bits
    return b64encode(key).decode('utf-8')

def encrypt_document(document_content, key):
    key = b64decode(key)
    cipher = AES.new(key, AES.MODE_GCM) # GCM mode provides authenticated encryption
    ciphertext, tag = cipher.encrypt_and_digest(document_content)
    return b64encode(cipher.nonce).decode('utf-8'), b64encode(ciphertext).decode('utf-8'), b64encode(tag).decode('utf-8')

def decrypt_document(nonce, ciphertext, tag, key):
    key = b64decode(key)
    nonce = b64decode(nonce)
    ciphertext = b64decode(ciphertext)
    tag = b64decode(tag)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    document_content = cipher.decrypt_and_verify(ciphertext, tag)
    return document_content

# AES-Based Digital Signature Functions
def sign_document(document_content, key):
    document_hash = hashlib.sha256(document_content).hexdigest()
    nonce, encrypted_hash, tag = encrypt_document(document_hash.encode('utf-8'), key)
    return {'nonce': nonce, 'encrypted_hash': encrypted_hash, 'tag': tag, 'document_hash': document_hash}

def verify_document_signature(document_content, key, signature):
    document_hash = hashlib.sha256(document_content).hexdigest()
    decrypted_hash = decrypt_document(signature['nonce'], signature['encrypted_hash'], signature['tag'], key).decode('utf-8')
    return decrypted_hash == document_hash