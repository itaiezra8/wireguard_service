import random
import string
from wireguard.utils.consts import PRIVATE_KEY_LENGTH


class Peer:
    
    def __init__(self, public_key: str, virtual_ip_address: str):
        self.public_key = public_key
        self.private_key = ''.join(random.choices(string.ascii_letters+string.digits, k=PRIVATE_KEY_LENGTH))
        self.virtual_ip_address = virtual_ip_address
        self.real_ip_address = '1.1.1.1'
