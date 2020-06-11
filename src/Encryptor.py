#This is the encrpytion handler file for PassLocker - Handles all encryption methods
#---------------------------------------------
#Author: Adam Thornes
#OS: Rasperian
#Date: 08/01/2019
#File Version: v3.0.0
#---------------------------------------------

import base64
import hashlib
import secrets, string
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

#Security Key --
securityKey = ""
#------------------------------
def BoolFromString(boolString):
    boolString = boolString.lower()
    if(boolString=="true" or boolString == "t" or boolString == "tru"):
        return True
    else:
        return False
def UpdateSecurityKey(newKey):
    global securityKey
    securityKey = newKey
    
def GetKey():
    return securityKey
    
#Password Generation
def GeneratePassword(requirements):
    #Define default parameters
    length = 15
    numbers = True
    specials = False
    uppercase = True
    lowercase = True
    
    if(len(requirements)>0):
        #Get requirements for password
        for requirement in requirements:
            require = requirement.split("=")
            if(len(require)==2):
                ti = require[0]                
                val = require[1]
                if(ti=="len"):                       
                    length = int(val)
                elif(ti=="num"):
                    numbers = BoolFromString(val)
                elif(ti=="spec"):
                    specials = BoolFromString(val)
                elif(ti=="upp"):
                    uppercase = BoolFromString(val)
                elif(ti=="low"):
                    lowercase = BoolFromString(val)
         
    #Build possible character sheet
    alphabet = ""
    if(uppercase) :   
        alphabet += string.ascii_uppercase
    if(lowercase):   
        alphabet += string.ascii_lowercase
    if(numbers):
        digitsToAdd = string.digits        
        alphabet += ''.join(c for c in digitsToAdd if c not in '~')
    if(specials):
        alphabet += string.punctuation
        
    genPassword = ''.join(secrets.choice(alphabet) for i in range(length))
    return genPassword
     
#File Protection

def GenerateSecurityKey():
    newKey = GenerateSALT()    
    return newKey
    
def ValidateSecurityKey(securityKey, fileKey, validationKey):    
    encKey = OneWayEncryptor(securityKey, validationKey) 
    if(encKey == fileKey):
        return True
    else:
        return False
        
def EncryptFile(fileContents, key):
    content=""
    for contents in fileContents:        
        content += contents + "<n>"
    encryptedFileString = AESEncrypt(content[:-3], key)
    return encryptedFileString
    
def DecryptFile(encryptedFileString, key):
    decryptedFileString = AESDecrypt(encryptedFileString, key)    
    content = decryptedFileString.split("<n>")   
    return content

#Password Encryption -------

def OneWayEncryptor(str, salt, dklen=32):
    #Encrypts a string with a given salt, returns encrypted string
    saltBytes = bytes(salt, 'utf-8')
    hmacBy = PBKDF2(str, saltBytes, dklen, 10000)       
    return "".join(map(chr,hmacBy))
    
def GenerateSALT(key_size=32, overrideSize=False):
    #Generate a cryptographically random salt key    
    if key_size not in [16, 24, 32] and overrideSize==False:
        raise ValueError('Bad AES key size')
    newSalt = Random.get_random_bytes(key_size) 
    return "".join(map(chr,newSalt))
    
def CheckPass(inputPass, encPass, salt):    
    if(encPass == OneWayEncryptor(inputPass, salt)):
        return True
    return False
    
def BindKey(longkey, shortkey):
    newKey = longkey[:len(longkey) // 2]
    newKey += shortkey
    newKey += longkey[:-(len(longkey) // 2)]
    return newKey
        
#AES Encrpytion ----------     

def EncodeString(str):
    return str.encode('utf-8')

def DecodeString(str):
    return str.decode('utf-8')

def AESEncrypt(source, key, encode=True):
    source = EncodeString(source)    
    key = EncodeString(key)
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data

def AESDecrypt(source, key, decode=True):
    key = EncodeString(key)
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return DecodeString(data[:-padding])  # remove the padding
     