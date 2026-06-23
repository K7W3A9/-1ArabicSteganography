import hashlib # مكتبةنستخدمها لتحويل كلمة المرور الى مفتاح قوي
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes  # يعطينا ارقام عشوائية قوية نستخدمها للسالت والاي في
from Crypto.Util.Padding import pad, unpad # نستخدمه لاضافة او ازالة حشو
#==============================================================
# دالة لتحويل كلمة المرور الى مفتاح تشفير قوي ليصبح كسرها صعب جدا على الهكر
# sha256 نوع الهاش
# password.encode('utf-8') تحويل النص الى بايت لان التشفير مايفهم نص
# salt رقم عشوائي يمنع الهجمات ,يعطي مفتاح مختلف كل مرة ,خاص بالمفتاح
# 100000 عداد التكرار
# dklen=32 طول المفتاح 
def derive_key(password, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
        dklen=32
    )

#===============================================================
# دالة تشفير النص 
# 
def encrypt_text(plaintext, password):

    salt = get_random_bytes(16) # انشاء سالت رقم عشوائي طولة 16 بايت  لمنع هجوم rainbow table attack

    key = derive_key(password, salt) # توليد المفتاح 

    iv = get_random_bytes(16) # انشاء اي في يجعل نفس النص يعطي تشفير مختلف كل مرة initialization vector

    cipher = AES.new(key, AES.MODE_CBC, iv) # cbc mode انشاء المشفر من نوع
    
    # نحول النص الى بايت ونضيف باديينج ونشفر
    ciphertext = cipher.encrypt(
        pad(plaintext.encode('utf-8'), AES.block_size) 
    )

    return salt + iv + ciphertext

#================================================================
# دالة استرجاع النص الاصلي
def decrypt_text(ciphertext_data, password):

    try:

        salt = ciphertext_data[0:16]

        iv = ciphertext_data[16:32]

        actual_ciphertext = ciphertext_data[32:]

        key = derive_key(password, salt)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_padded_data = cipher.decrypt(actual_ciphertext)

        return unpad(
            decrypted_padded_data,
            AES.block_size
        ).decode('utf-8')

    except Exception as e:

        print("Decryption error:", e)

        return None