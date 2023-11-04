import requests
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

# 设置签名密钥
sign_key = 'd3dGiJc651gSQ8w1'

# 设置参数
params = {
    'id': 'bid',  # 这里替换为实际的bid
    'chapterId': 'chapterId'  # 这里替换为实际的chapterId
}

# 生成签名
param_sign = hashlib.md5(''.join(f'{k}={v}' for k, v in sorted(params.items())).encode() + sign_key.encode()).hexdigest()
params['sign'] = param_sign

# 发送请求
url = "https://api-ks.wtzw.com/api/v1/chapter/content"
response = requests.get(url, params=params)

# 解密响应
def decode(content):
    iv_enc_data = base64.b64decode(content)
    key = hashlib.md5('242ccb8230d709e1'.encode()).digest()
    iv = iv_enc_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(iv_enc_data[16:]), AES.block_size)
    return decrypted.decode()

data = response.json()['data']['content']
print(decode(data))
