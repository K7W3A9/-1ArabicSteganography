import cv2
import numpy as np
from scipy.stats import entropy

# =========================
# Chi-Square Attack (FIXED)
# =========================
def histogram_attack_test(original, stego):

    orig_hist = cv2.calcHist([original], [0], None, [256], [0, 256]).flatten()
    stego_hist = cv2.calcHist([stego], [0], None, [256], [0, 256]).flatten()

    chi_square = 0

    for i in range(len(orig_hist)):
        if orig_hist[i] > 0:  #  تجاهل القيم صفر
            chi_square += ((stego_hist[i] - orig_hist[i]) ** 2) / orig_hist[i]

    return chi_square


# =========================
# RS Analysis (كما هو)
# =========================
def rs_steganalysis(image):

    def flip_lsb(block):
        return block ^ 1

    def discriminant(block):
        return np.sum(np.abs(np.diff(block.flatten())))

    rows, cols = image.shape[:2]

    regular = 0
    singular = 0

    for _ in range(100):

        x = np.random.randint(0, rows - 8)
        y = np.random.randint(0, cols - 8)

        block = image[x:x+8, y:y+8, 0]

        d_original = discriminant(block)
        d_flipped = discriminant(flip_lsb(block))

        if d_flipped > d_original:
            regular += 1
        elif d_flipped < d_original:
            singular += 1

    rs_ratio = abs(regular - singular) / 100

    return rs_ratio


# =========================
# Entropy Analysis (FIXED)
# =========================
def entropy_analysis(original, stego):

    # 🔥 تحويل إلى grayscale
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    stego_gray = cv2.cvtColor(stego, cv2.COLOR_BGR2GRAY)

    # histogram
    orig_hist = cv2.calcHist([original_gray], [0], None, [256], [0, 256]).flatten()
    stego_hist = cv2.calcHist([stego_gray], [0], None, [256], [0, 256]).flatten()

    # تحويل إلى احتمالات
    orig_prob = orig_hist / np.sum(orig_hist)
    stego_prob = stego_hist / np.sum(stego_hist)

    # حساب entropy
    orig_entropy = entropy(orig_prob)
    stego_entropy = entropy(stego_prob)

    change = abs(orig_entropy - stego_entropy)

    return orig_entropy, stego_entropy, change


