import public as p

text = p.get_qimao('208895', '16498371000772', '7b0a28dd183ef93afeb2e0af5e3b4e01')
print(text)
text2 = text['data']['content']
result = p.decrypt_qimao(text2)
print(result)
