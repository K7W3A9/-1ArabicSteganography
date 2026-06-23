import numpy as np
import cv2
import hashlib

# =========================
# Classical LSB
# =========================

def classical_lsb_embed(image, bits):
    stego = image.copy()
    rows, cols, channels = stego.shape

    length_bits = format(len(bits), '032b')
    full_bits = length_bits + bits

    bit_index = 0

    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                if bit_index >= len(full_bits):
                    return stego

                stego[r, c, ch] = (stego[r, c, ch] & 0xFE) | int(full_bits[bit_index])
                bit_index += 1

    return stego


def classical_lsb_extract(image):
    rows, cols, channels = image.shape

    length_bits = ""
    bit_index = 0

    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                if bit_index < 32:
                    length_bits += str(image[r, c, ch] & 1)
                    bit_index += 1

                    if bit_index == 32:
                        break
            if bit_index == 32:
                break
        if bit_index == 32:
            break

    data_length = int(length_bits, 2)

    data_bits = ""
    bit_index = 0

    for r in range(rows):
        for c in range(cols):
            for ch in range(channels):
                if bit_index < 32:
                    bit_index += 1
                    continue

                if len(data_bits) >= data_length:
                    return data_bits

                data_bits += str(image[r, c, ch] & 1)

    return data_bits


# =========================
# Adaptive LSB
# =========================

def adaptive_lsb_embed(image, bits, key):
    stego = image.copy()

    image_msb = image & 0xFE
    gray = cv2.cvtColor(image_msb, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    texture = np.abs(lap)

    threshold = 20
    positions = []

    rows, cols = texture.shape

    for r in range(rows):
        for c in range(cols):
            if texture[r, c] > threshold:
                positions.append((r, c))

    positions = np.array(positions)

    seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)

    shuffled_positions = positions[rng.permutation(len(positions))]

    length_bits = format(len(bits), '032b')
    full_bits = length_bits + bits

    bit_index = 0

    for r, c in shuffled_positions:
        for ch in range(3):
            if bit_index >= len(full_bits):
                return stego

            stego[r, c, ch] = (stego[r, c, ch] & 0xFE) | int(full_bits[bit_index])
            bit_index += 1

    return stego

