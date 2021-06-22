import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
# generar hash seguro

def cif(password):
    salt = os.urandom(16)
    passbytes = password.encode('utf-8')
    kdf = Scrypt(salt=salt, length=32,
               n=2**14, r=8, p=1,
               backend=default_backend())
    key = kdf.derive (passbytes)
    return (key.hex())

def des(password,key,salt):
    passbin = password.encode('utf-8')
    keybin = bytes.fromhex(key)
    saltbin = bytes.fromhex(salt)
    
    kdf = Scrypt(salt=saltbin, length=32,
               n=2**14, r=8, p=1,
               backend=default_backend())
    kdf.verify(passbin, keybin)

    
#if __name__ == '__main__':
#    password='passhash'
#    passh = cif(password)
#    print(passh)
