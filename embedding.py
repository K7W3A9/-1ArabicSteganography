import cv2
import numpy as np
import hashlib
import re


# =========================
# TEXT PROCESSING 
# =========================

# ازالة التشكيل
def arabic_preprocess(text):

    tashkeel = re.compile(r'[\u064B-\u065F]')
    text = re.sub(tashkeel, '', text)

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    text = text.replace("ـ", "")
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# تقسيم النص الى مهم وعادي
def encode_priority(text):

    words = text.split()

    stop_words = {
        "في","من","الى","على","و","او","ثم","قد","كان","كانت",
        "هو","هي","هذا","هذه","ذلك","هناك"
    }

    important_words = []
    normal_words = []
    template = []

    for w in words:
        if w in stop_words:
            normal_words.append(w)
            template.append('N')
        else:
            important_words.append(w)
            template.append('I')

    template_str = ''.join(template)

    return template_str + "|||" + " ".join(important_words) + "|||" + " ".join(normal_words)


# اعادة بناء النص بعد الاستخراج
def decode_priority(text):

    if "|||" not in text:
        return text

    parts = text.split("|||")

    if len(parts) != 3:
        return text

    template_str = parts[0]
    important_words = parts[1].split()
    normal_words = parts[2].split()

    result = []
    i_idx = 0
    n_idx = 0

    for marker in template_str:
        if marker == 'I':
            result.append(important_words[i_idx])
            i_idx += 1
        else:
            result.append(normal_words[n_idx])
            n_idx += 1

    return " ".join(result)


# =========================
# BIT FUNCTIONS
# =========================

# تحويل البيانات الى بتات
def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

# تحويل البتات الى بايتات
def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


# =========================
# REGION DETECTION
# =========================

# تقسيم الصورة الى مناطق قوية ومناطق ضعيفة
def get_dual_regions(image, high_thresh=30, low_thresh=10):

    image_msb = image & 0xFE
    gray = cv2.cvtColor(image_msb, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    texture = np.abs(lap)

    high = []
    low = []

    rows, cols = texture.shape

    for r in range(rows):
        for c in range(cols):

            if texture[r, c] > high_thresh:
                high.append((r, c))
            elif texture[r, c] > low_thresh:
                low.append((r, c))

    # fallback
    if len(high) == 0 and len(low) == 0:
        print(" fallback → full image")
        for r in range(rows):
            for c in range(cols):
                low.append((r, c))

    return np.array(high), np.array(low)


# =========================
# EMBEDDING
# =========================

# إخفاء النص داخل الصورة
def embed_semantic(image_path, important_bits, normal_bits, output_path, key):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("لا يمكن فتح الصورة ")

    # إضافة الطول (32 بت)
    important_bits = format(len(important_bits), '032b') + important_bits
    normal_bits = format(len(normal_bits), '032b') + normal_bits

    # استخراج المناطق
    high_regions, low_regions = get_dual_regions(image)

    if len(high_regions) == 0:
        high_regions = low_regions.copy()

    if len(low_regions) == 0:
        low_regions = high_regions.copy()

    #  فحص السعة 
    if len(important_bits) > len(high_regions) * 3:
        raise ValueError("❌ البيانات المهمة أكبر من سعة المناطق القوية")

    if len(normal_bits) > len(low_regions) * 3:
        raise ValueError("❌ البيانات العادية أكبر من سعة المناطق الضعيفة")

    # shuffle باستخدام المفتاح
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)

    high_regions = high_regions[rng.permutation(len(high_regions))]
    low_regions = low_regions[rng.permutation(len(low_regions))]

    stego = image.copy()

    # إخفاء المهم
    i = 0
    for r, c in high_regions:
        for ch in range(3):
            if i >= len(important_bits):
                break
            stego[r, c, ch] = (stego[r, c, ch] & 0xFE) | int(important_bits[i])
            i += 1
        if i >= len(important_bits):
            break

    #  إخفاء العادي
    j = 0
    for r, c in low_regions:
        for ch in range(3):
            if j >= len(normal_bits):
                break
            stego[r, c, ch] = (stego[r, c, ch] & 0xFE) | int(normal_bits[j])
            j += 1
        if j >= len(normal_bits):
            break

    cv2.imwrite(output_path, stego)

    return output_path

# =========================
# CAPACITY
# =========================
# حساب سعة الصورة 
def calculate_capacity(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Cannot open image")

    height, width = image.shape[:2]

    high_regions, low_regions = get_dual_regions(image)

    total_capacity = (len(high_regions) + len(low_regions)) * 3

    usable_bits = max(0, total_capacity - 64)

    return {
        "adaptive_pixels": len(high_regions) + len(low_regions),
        "bits": usable_bits,
        "chars": usable_bits // 8,
        "width": width,
        "height": height
    }