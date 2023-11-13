import hashlib
import public as p

book_id = '1432205_0'
chapter_id = '27906684'
param_string = f"chapterId={chapter_id}id={book_id}{p.sign_key}"
sign = hashlib.md5(param_string.encode()).hexdigest()
encrypted_content = p.get_qimao(book_id, chapter_id, sign)
print(encrypted_content)