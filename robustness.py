import cv2
import numpy as np
import os

def apply_attacks(stego_img):

    attacks = {}

    # =========================
    # JPEG
    # =========================
    jpeg_path = os.path.join("uploads", "temp_jpeg.jpg")

    cv2.imwrite(
        jpeg_path,
        stego_img,
        [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    )

    attacks["jpeg"] = cv2.imread(jpeg_path)

    # =========================
    # Noise
    # =========================
    noise = np.random.normal(
        0,
        10,
        stego_img.shape
    ).astype(np.float32)

    noise_img = np.clip(
        stego_img.astype(np.float32) + noise,
        0,
        255
    ).astype(np.uint8)

    attacks["noise"] = noise_img

    # =========================
    # Crop
    # =========================
    h, w = stego_img.shape[:2]

    crop = stego_img[
        0:int(h * 0.9),
        0:int(w * 0.9)
    ]

    crop_img = cv2.resize(crop, (w, h))

    attacks["crop"] = crop_img

    return attacks