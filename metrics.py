import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim


# =========================
# PSNR
# =========================
def calculate_psnr(original, stego):

    if original is None or stego is None:
        raise ValueError("إحدى الصور غير موجودة")

    mse = np.mean((original.astype(np.float64) - stego.astype(np.float64)) ** 2)

    if mse == 0:
        return float('inf')

    return 20 * np.log10(255.0 / np.sqrt(mse))


# =========================
# SSIM
# =========================
def calculate_ssim(original, stego):

    if original is None or stego is None:
        raise ValueError("إحدى الصور غير موجودة")

    if len(original.shape) == 3:
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        stego_gray = cv2.cvtColor(stego, cv2.COLOR_BGR2GRAY)
    else:
        original_gray = original
        stego_gray = stego

    score, _ = ssim(original_gray, stego_gray, full=True)
    return score


# =========================
# BER (CORRECT VERSION)
# =========================
def calculate_ber(original_bits, extracted_bits):

    if len(original_bits) == 0 or len(extracted_bits) == 0:
        return 1.0

    min_len = min(len(original_bits), len(extracted_bits))

    errors = sum(
        b1 != b2
        for b1, b2 in zip(original_bits[:min_len], extracted_bits[:min_len])
    )

    return errors / min_len


# =========================
# NORMALIZED PAYLOAD (BPP)
# =========================
def calculate_payload(total_bits, image_shape):

    h, w = image_shape[:2]
    total_pixels = h * w * 3  # RGB channels

    return total_bits / total_pixels