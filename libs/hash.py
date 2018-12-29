# __author__ = itsneo1990
from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES
from django.conf import settings
from hashlib import md5


def encrypt(text):
    """
    加密函数
    如果text不足16位就用空格补足为16位，
    如果大于16当时不是16的倍数，那就补足为16的倍数。
    """
    text = text.encode('utf-8')
    crypto = AES.new(settings.CRYPT_SECRET.encode('utf-8'), AES.MODE_CBC, b'0000000000000000')
    length = 16
    count = len(text)
    if count < length:
        add = (length - count)
        text = text + ('\0' * add).encode('utf-8')
    elif count > length:
        add = (length - (count % length))
        text = text + ('\0' * add).encode('utf-8')
    ciphered = crypto.encrypt(text)
    return b2a_hex(ciphered)


def decrypt(text):
    text = text.encode('utf-8')
    crypto = AES.new(settings.CRYPT_SECRET.encode('utf-8'), AES.MODE_CBC, b'0000000000000000')
    plain_text = crypto.decrypt(a2b_hex(text))
    # return plain_text.rstrip(b'\0').decode()
    return bytes.decode(plain_text).rstrip('\0')


def get_md5(text):
    wrapper = md5()
    wrapper.update(text)
    return wrapper.hexdigest()
