import base64
import crypto
import sys
sys.modules['Crypto'] = crypto
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import conf

class AesUtil():
    def __init__(self):
        self.key = conf.config['encrypt_key']

    def encrypt(self, data):
        iv =  get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv)
        return base64.b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'), 
            AES.block_size))).decode('utf-8')

    def decrypt(self, data):
        raw = base64.b64decode(data)
        self.cipher = AES.new(self.key.encode(), AES.MODE_CBC, raw[:AES.block_size])
        return str(unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size), 'utf-8')