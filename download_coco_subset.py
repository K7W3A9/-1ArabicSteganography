import os
import urllib.request
import cv2
import socket
import random

NUM_IMAGES = 85
BASE_URL = "http://images.cocodataset.org/val2017/"

SAVE_DIR = "admin/dataset"
os.makedirs(SAVE_DIR, exist_ok=True)

count = 0

socket.setdefaulttimeout(10)

print("Downloading images...")

while count < NUM_IMAGES:

    i = random.randint(0, 50000)  # 🔥 رقم عشوائي

    image_name = f"{i:012d}.jpg"
    url = BASE_URL + image_name

    jpg_path = os.path.join(SAVE_DIR, image_name)
    png_path = jpg_path.replace(".jpg", ".png")

    try:
        urllib.request.urlretrieve(url, jpg_path)

        img = cv2.imread(jpg_path)

        if img is None:
            os.remove(jpg_path)
            continue

        cv2.imwrite(png_path, img)
        os.remove(jpg_path)

        print(f"✔ {count+1}/{NUM_IMAGES} -> {image_name}")

        count += 1

    except:
        pass

print(f"\n✅ Done! Downloaded {count} images.")