import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode


# Blockchain classes
class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        print(f"Block created - Index: {index}, Previous Hash: {previous_hash}, Timestamp: {timestamp}, Data: {data}, Hash: {hash}")

    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, data):
        return hashlib.sha256(f"{index}{previous_hash}{timestamp}{data}".encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        print("Blockchain created with genesis block: ", self.chain)

    def create_genesis_block(self):
        return Block(0, "0", int(time.time()), "Genesis Block", Block.calculate_hash(0, "0", int(time.time()), "Genesis Block"))

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(latest_block.index + 1, latest_block.hash, int(time.time()), data, Block.calculate_hash(latest_block.index + 1, latest_block.hash, int(time.time()), data))
        self.chain.append(new_block)
        print("New block added - Index: ", new_block.index, ", Hash: ", new_block.hash)
        return new_block

# Initialize Blockchain
blockchain = Blockchain()

# Document hashing and upload functions
def hash_document(document):
    document_hash = hashlib.sha256(document).hexdigest()
    print("Calculated document hash:", document_hash)
    return document_hash

def upload_document(document_content):
    document_hash = hash_document(document_content)
    blockchain.add_block(document_hash)
    print("Block added to blockchain. Current chain length:", len(blockchain.chain))
    return document_hash


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
