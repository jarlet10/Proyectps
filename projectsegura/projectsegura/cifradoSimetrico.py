
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import sys
from getpass import getpass

###### se recibe el password en cadena y se derivaa una llave ######
def generar_llave_aes_from_password(password):
    password = password.encode('utf-8')
    derived_key = HKDF(algorithm=hashes.SHA256(),
                       length=32,
                       salt=None,
                       info=b'handshake data ',
                       backend=default_backend()).derive(password)
    return derived_key
#resultado de llave en binario


####################### Cifrar y descifrar ###########################

def cifrar(mesage, llavepas, iv):   
    llave_aes = generar_llave_aes_from_password(llavepas)
    mensaje = bytes(mesage, 'utf-8')
    aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv),
                       backend=default_backend())
    cifrador = aesCipher.encryptor()
    cifrado = cifrador.update(mensaje)
    cifrador.finalize()
    return cifrado

def descifrar(cifrado1, llavepas, iv1): #passc es la pas cifrada
    cifrado = base64.b64decode(cifrado1)
    iv = base64.b64decode(iv1)
    llave_aes = generar_llave_aes_from_password(llavepas)
    aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv),
                       backend=default_backend())
    descifrador = aesCipher.decryptor()
    plano = descifrador.update(cifrado)
    descifrador.finalize()
    return plano.decode('utf-8')

######################################################################

if __name__ == '__main__':
    print('~~~~~ Cifrado ~~~~~')
    passwordc = 'passpass'
    passwordm = 'PasMaster#1'
    iv = os.urandom(16)
    print(passwordc)
    print(passwordm)
    print(iv)
    #llave = generar_llave_aes_from_password(passwordm)
    #print(llave)
    cifrado=cifrar(passwordc,passwordc,iv)
    print(cifrado)
