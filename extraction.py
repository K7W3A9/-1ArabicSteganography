import cv2
import numpy as np
import hashlib

from embedding import get_dual_regions, bits_to_bytes, decode_priority
from encryption import decrypt_text


def _extract_region_bits(image, regions, key):
    """
    استخراج البتات من منطقة معينة (high أو low).
    يقرأ أول 32 بت كطول، ثم يستخرج البيانات حسب الطول.
    """
    # قراءة الطول (32 بت)
    length_bits = ""
    count = 0
    for r, c in regions:
        for ch in range(3):
            length_bits += str(image[r, c, ch] & 1)
            count += 1
            if count == 32:
                break
        if count == 32:
            break

    data_length = int(length_bits, 2)

    # قراءة البيانات
    data_bits = ""
    count = 0
    for r, c in regions:
        for ch in range(3):
            count += 1
            if count <= 32:
                continue
            data_bits += str(image[r, c, ch] & 1)
            if len(data_bits) == data_length:
                break
        if len(data_bits) == data_length:
            break

    return data_bits


def extract_semantic(stego_image_path, key, return_bits=False):

    image = cv2.imread(stego_image_path)
    if image is None:
        raise ValueError("Cannot open image")

    # تحديد المناطق
    high_regions, low_regions = get_dual_regions(image)

    if len(high_regions) == 0:
        high_regions = low_regions.copy()
    if len(low_regions) == 0:
        low_regions = high_regions.copy()

    # نفس ترتيب الإخفاء
    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)

    high_regions = high_regions[rng.permutation(len(high_regions))]
    low_regions = low_regions[rng.permutation(len(low_regions))]

    # استخراج البتات
    bits_high = _extract_region_bits(image, high_regions, key)
    bits_low = _extract_region_bits(image, low_regions, key)

    # 🔥 إذا تريد BER → رجع البتات مباشرة
    if return_bits:
        return bits_high + bits_low

    # فك التشفير (كما هو)
    data_high = bits_to_bytes(bits_high)
    data_low = bits_to_bytes(bits_low)

    text_high = decrypt_text(data_high, key) or ""
    text_low = decrypt_text(data_low, key) or ""

    combined = text_high + "|||" + text_low

    return decode_priority(combined)
