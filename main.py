import os
import cv2
import numpy as np
import metrics
import baseline
import security_metrics
import encryption
import embedding
import extraction
import robustness
from flask import Flask, request, send_from_directory, jsonify
import threading
from werkzeug.utils import secure_filename


app = Flask(__name__)

evaluation_progress = {
    "running": False,
    "finished": False,
    "progress": 0,
    "current": 0,
    "total": 0,
    "results": []
}

cancel_requested = False

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- PASSWORD ----------------
PASSWORD = "mysecretpassword"

# =========================
# TEST TEXT
# =========================

TEST_TEXT = ( """   
            إِنَّ هَذَا النِّظَامَ يُعَدُّ مِنَ الأَنْظِمَةِ المُتَقَدِّمَةِ فِي مَجَالِ إِخْفَاءِ البَيَانَاتِ دَاخِلَ الصُّوَرِ الرَّقْمِيَّةِ،
            حَيْثُ يَسْتَخْدِمُ تَقْنِيَاتٍ ذَكِيَّةً لِتَحْلِيلِ مَحْتَوَى الصُّورَةِ وَتَحْدِيدِ المَنَاطِقِ المُنَاسِبَةِ لِزَرْعِ
            المَعْلُومَاتِ بِطَرِيقَةٍ غَيْرِ مَرْئِيَّةٍ لِلعَيْنِ البَشَرِيَّةِ، مَعَ الحِفَاظِ عَلَى جَوْدَةِ الصُّورَةِ وَتَقْلِيلِ
            التَّشْوِيهِ إِلَى أَدْنَى حَدٍّ مُمْكِنٍ. كَمَا يَعْمَلُ النِّظَامُ عَلَى تَشْفِيرِ البَيَانَاتِ بِاسْتِخْدَامِ خَوَارِزْمِيَّاتٍ
            قَوِيَّةٍ مِثْلَ AES، مِمَّا يَضْمَنُ سِرِّيَّةَ المَعْلُومَاتِ وَعَدَمَ القُدْرَةِ عَلَى اسْتِرْجَاعِهَا دُونَ المِفْتَاحِ الصَّحِيحِ.
            وَيَعْتَمِدُ النِّظَامُ أَيْضًا عَلَى تَقْسِيمِ النَّصِّ إِلَى أَجْزَاءٍ مُهِمَّةٍ وَأُخْرَى عَادِيَّةٍ، حَيْثُ يُتِمُّ
            إِخْفَاءُ الأَجْزَاءِ المُهِمَّةِ فِي المَنَاطِقِ ذَاتِ التَّفَاصِيلِ العَالِيَةِ، بَيْنَمَا تُخَزَّنُ الأَجْزَاءُ الأَقَلُّ
            أَهَمِّيَّةً فِي المَنَاطِقِ الأَقَلِّ حَسَاسِيَّةً. هَذَا التَّوْزِيعُ الذَّكِيُّ يُسَاهِمُ فِي زِيَادَةِ الأَمَانِ وَتَقْلِيلِ
            إِمْكَانِيَّةِ اكْتِشَافِ البَيَانَاتِ المُخْفَاةِ. كَمَا يَتَضَمَّنُ النِّظَامُ آلِيَّةً لِاكْتِشَافِ الهُجُومَاتِ مِثْلَ
            الضَّغْطِ وَإِضَافَةِ الضَّوْضَاءِ أَوِ القَصِّ، مِمَّا يَجْعَلُهُ أَكْثَرَ قُدْرَةً عَلَى التَّحَمُّلِ وَالمُقَاوَمَةِ.

            يَعْتَمِدُ هَذَا الأُسْلُوبُ عَلَى تَقْسِيمِ البَيَانَاتِ بِشَكْلٍ دِينَامِيكِيٍّ وَفْقًا لِطَبِيعَةِ المُحْتَوَى،
            حَيْثُ تُصَنَّفُ الكَلِمَاتُ وَالعِبَارَاتُ إِلَى عَنَاصِرَ ذَاتِ أَهَمِّيَّةٍ عَالِيَةٍ وَأُخْرَى ثَانَوِيَّةٍ،
            مِمَّا يُسَاهِمُ فِي تَحْسِينِ عَمَلِيَّةِ الإِخْفَاءِ وَتَقْلِيلِ التَّأْثِيرِ عَلَى القِيَمِ اللَّوْنِيَّةِ لِلصُّورَةِ.
            كَمَا يَسْمَحُ هَذَا الأُسْلُوبُ بِالحِفَاظِ عَلَى جَوْدَةِ الصُّورَةِ حَتَّى مَعَ زِيَادَةِ كَمِّيَّةِ البَيَانَاتِ المُخْفَاةِ،
            الأَمْرُ الَّذِي يُحَقِّقُ تَوَازُنًا بَيْنَ السَّعَةِ وَالأَمَانِ وَعَدَمِ القَابِلِيَّةِ لِلاكْتِشَافِ.

            وَيَتِمُّ اخْتِيَارُ المَنَاطِقِ المُسْتَخْدَمَةِ فِي الإِخْفَاءِ بِالاعْتِمَادِ عَلَى تَحْلِيلِ القَوَامِ وَالتَّفَاصِيلِ
            فِي الصُّورَةِ، حَيْثُ تُسْتَخْدَمُ المَنَاطِقُ ذَاتُ التَّغَيُّرَاتِ العَالِيَةِ لِإِخْفَاءِ البَيَانَاتِ المُهِمَّةِ،
            لِأَنَّ التَّغْيِيرَاتِ البَسِيطَةَ فِيهَا تَكُونُ أَقَلَّ قَابِلِيَّةً لِلْمُلَاحَظَةِ مِنْ قِبَلِ العَيْنِ البَشَرِيَّةِ.
            أَمَّا المَنَاطِقُ الأَقَلُّ تَعْقِيدًا فَيُسْتَخْدَمُ فِيهَا إِخْفَاءُ البَيَانَاتِ الأَقَلِّ أَهَمِّيَّةً،
            مِمَّا يُقَلِّلُ مِنْ إِمْكَانِيَّةِ اكْتِشَافِ البَيَانَاتِ بِاسْتِخْدَامِ أَدَوَاتِ التَّحْلِيلِ الإِحْصَائِيِّ.

            وَيَسْتَخْدِمُ النِّظَامُ تَقْنِيَاتِ تَشْفِيرٍ مُتَقَدِّمَةً لِضَمَانِ سِرِّيَّةِ الرَّسَالَةِ المُخْفَاةِ،
            حَيْثُ يَتِمُّ تَحْوِيلُ النَّصِّ إِلَى بَيَانَاتٍ مُشَفَّرَةٍ قَبْلَ عَمَلِيَّةِ الإِخْفَاءِ،
            وَبِالتَّالِي فَإِنَّ اسْتِخْرَاجَ البَيَانَاتِ دُونَ المِفْتَاحِ الصَّحِيحِ يُعَدُّ أَمْرًا صَعْبًا جِدًّا.
            كَذَلِكَ يَعْمَلُ النِّظَامُ عَلَى تَقْلِيلِ التَّغَيُّرَاتِ الإِحْصَائِيَّةِ الَّتِي تَحْدُثُ فِي تَوْزِيعِ البِكْسِلَاتِ،
            وَهُوَ مَا يُسَاهِمُ فِي تَقْلِيلِ فُرَصِ اكْتِشَافِ البَيَانَاتِ المُخْفَاةِ بِوَاسِطَةِ اخْتِبَارَاتِ
            Chi-Square وَRS Analysis وَغَيْرِهَا مِنْ أَدَوَاتِ التَّحْلِيلِ الجِنَائِيِّ الرَّقْمِيِّ.

            إِضَافَةً إِلَى ذَلِكَ، فَإِنَّ النِّظَامَ يُرَاعِي التَّوَازُنَ بَيْنَ الأَمَانِ وَالأَدَاءِ،
            حَيْثُ يَسْتَطِيعُ التَّعَامُلَ مَعَ أَحْجَامٍ مُخْتَلِفَةٍ مِنَ الصُّوَرِ وَالنُّصُوصِ،
            مَعَ الحِفَاظِ عَلَى سُرْعَةِ المُعَالَجَةِ وَدِقَّةِ الاسْتِخْرَاجِ.
            كَمَا أَنَّ النِّظَامَ يُسَاهِمُ فِي تَوْفِيرِ بِيئَةٍ آمِنَةٍ لِنَقْلِ البَيَانَاتِ الحَسَّاسَةِ،
            خُصُوصًا فِي التَّطْبِيقَاتِ الَّتِي تَتَطَلَّبُ سِرِّيَّةً عَالِيَةً وَحِمَايَةً مِنَ المُرَاقَبَةِ وَالتَّحْلِيلِ.

            وَقَدْ أَظْهَرَتِ التَّجَارِبُ أَنَّ النِّظَامَ يُحَقِّقُ قِيَمًا مُرْتَفِعَةً فِي مَقَايِيسِ
            PSNR وَSSIM، مِمَّا يَدُلُّ عَلَى الحِفَاظِ عَلَى جَوْدَةِ الصُّورَةِ بَعْدَ الإِخْفَاءِ،
            كَمَا أَنَّهُ يُحَقِّقُ مُعَدَّلَ خَطَأٍ مُنْخَفِضًا فِي BER عِنْدَ عَدَمِ وُجُودِ هُجُومَاتٍ،
            وَهُوَ مَا يُؤَكِّدُ كَفَاءَةَ عَمَلِيَّةِ الإِخْفَاءِ وَالاِسْتِرْجَاعِ فِي الظُّرُوفِ الطَّبِيعِيَّةِ.
                            """)

@app.route('/dataset/<path:filename>')
def dataset_files(filename):
    return send_from_directory('admin/dataset', filename)



# ---------------- CHECK CAPACITY ----------------

@app.route('/check_capacity', methods=['POST'])
def check_capacity():

    try:
        image_file = request.files['image']

        filename = secure_filename(image_file.filename)

        image_path = os.path.join(UPLOAD_FOLDER, filename)

        image_file.save(image_path)

        capacity = embedding.calculate_capacity(image_path)

        return jsonify({
            "status": "success",
            **capacity
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# ---------------- USER ----------------

@app.route('/')
def index():
    return send_from_directory("user", "a4 (2).html")


@app.route('/user/<path:filename>')
def user_static(filename):
    return send_from_directory("user", filename)


# ---------------- ADMIN ----------------

@app.route('/admin/')
def admin_index():
    return send_from_directory("admin", "index_admin.html")


@app.route('/admin/<path:filename>')
def admin_static(filename):
    return send_from_directory("admin", filename)


# ---------------- UPLOADS ----------------

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------- ENCODE ----------------

@app.route('/encode', methods=['POST'])
def encode():

    try:
        text = request.form['text']
        password = request.form['password']
        image_file = request.files['image']

        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        clean_text = embedding.arabic_preprocess(text)
        combined_text = embedding.encode_priority(clean_text)

        parts = combined_text.split("|||")
        if len(parts) != 3:
            return jsonify({"status": "error", "message": "❌ خطأ في تقسيم النص"})

        template_str, important_text, normal_text = parts

        important_encrypted = encryption.encrypt_text(
            template_str + "|||" + important_text, password
        )

        normal_encrypted = encryption.encrypt_text(normal_text, password)

        important_bits = embedding.bytes_to_bits(important_encrypted)
        normal_bits = embedding.bytes_to_bits(normal_encrypted)

        capacity = embedding.calculate_capacity(image_path)
        total_bits = len(important_bits) + len(normal_bits) + 64

        if total_bits > capacity["bits"]:
            return jsonify({
                "status": "error",
                "message": f"❌ النص كبير جداً! الحد الأقصى: {capacity['chars']} حرف"
            })

        output_path = os.path.join(
            UPLOAD_FOLDER,
            os.path.splitext(filename)[0] + "_stego.png"
        )

        embedding.embed_semantic(
            image_path,
            important_bits,
            normal_bits,
            output_path,
            password
        )

        return jsonify({
            "status": "success",
            "filename": os.path.basename(output_path)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ---------------- DECODE ----------------

@app.route('/decode', methods=['POST'])
def decode():

    try:
        image_file = request.files['image']
        password = request.form['password']

        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        text = extraction.extract_semantic(image_path, password)

        if text is None or "|||" in text:
            raise ValueError("❌ كلمة المرور خاطئة أو البيانات تالفة")

        return jsonify({"status": "success", "text": text})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



@app.route('/admin/admin_encode', methods=['POST'])
def admin_encode():
    try:
        text = request.form['text']
        image_file = request.files['image']

        original_path = os.path.join(UPLOAD_FOLDER, "original.png")
        stego_path = os.path.join(UPLOAD_FOLDER, "stego.png")
        image_file.save(original_path)

        # 1. تنظيف النص
        clean_text = embedding.arabic_preprocess(text)

        # 2. تقسيم النص
        combined_text = embedding.encode_priority(clean_text)
        parts = combined_text.split("|||")
        if len(parts) != 3:
            return "❌ Error: تقسيم النص غير صحيح"

        template_str = parts[0]
        important_text = parts[1]
        normal_text = parts[2]

        # 3. التشفير
        important_encrypted = encryption.encrypt_text(template_str + "|||" + important_text, PASSWORD)
        normal_encrypted = encryption.encrypt_text(normal_text, PASSWORD)

        # 4. تحويل إلى بتات
        important_bits = embedding.bytes_to_bits(important_encrypted)
        normal_bits = embedding.bytes_to_bits(normal_encrypted)

        # 5. التحقق من السعة
        capacity = embedding.calculate_capacity(original_path)
        total_bits = len(important_bits) + len(normal_bits) + 64
        if total_bits > capacity["bits"]:
            return f"❌ النص كبير جداً! الحد الأقصى: {capacity['chars']} حرف"


        # 6. الإخفاء
        embedding.embed_semantic(
            original_path,
            important_bits,
            normal_bits,
            stego_path,
            PASSWORD
        )

       # =========================
        # حساب ORIGINAL
        # =========================
        original_img = cv2.imread(original_path)
        stego_img_clean = cv2.imread(stego_path)

        psnr = metrics.calculate_psnr(original_img, stego_img_clean)
        ssim = metrics.calculate_ssim(original_img, stego_img_clean)

        extracted_bits = extraction.extract_semantic(stego_path, PASSWORD, return_bits=True)
        original_bits = important_bits + normal_bits
        ber = metrics.calculate_ber(original_bits, extracted_bits)


        # =========================
        # ROBUSTNESS TESTS
        # =========================

        attacks = robustness.apply_attacks(stego_img_clean)

        results = {}

        for attack_name, attack_img in attacks.items():

            print(attack_name, attack_img.shape if attack_img is not None else "NONE")

            # حساب PSNR + SSIM
            attack_psnr, attack_ssim = safe_metrics(original_img, attack_img)

            # حفظ مؤقت للصورة
            temp_path = os.path.join(
                UPLOAD_FOLDER,
                f"{attack_name}.png"
            )

            cv2.imwrite(temp_path, attack_img)

            # استخراج البتات
            extracted_attack_bits = extraction.extract_semantic(
                temp_path,
                PASSWORD,
                return_bits=True
            )

            # حساب BER
            attack_ber = metrics.calculate_ber(
                original_bits,
                extracted_attack_bits
            )

            # تخزين النتائج
            results[attack_name] = {
                "psnr": round(attack_psnr, 2),
                "ssim": round(attack_ssim, 4),
                "ber": round(attack_ber, 6)
            }

        # =========================
        # رجّع JSON
        # =========================
        return jsonify({

        # Original
        "psnr": round(psnr,2),
        "ssim": round(ssim,4),
        "ber": round(ber,6),

        # JPEG
        "psnr_jpeg": results["jpeg"]["psnr"],
        "ssim_jpeg": results["jpeg"]["ssim"],
        "ber_jpeg": results["jpeg"]["ber"],

        # Noise
        "psnr_noise": results["noise"]["psnr"],
        "ssim_noise": results["noise"]["ssim"],
        "ber_noise": results["noise"]["ber"],

        # Crop
        "psnr_crop": results["crop"]["psnr"],
        "ssim_crop": results["crop"]["ssim"],
        "ber_crop": results["crop"]["ber"],
    })

    except Exception as e:
        return jsonify({"error": str(e)})

def safe_metrics(img1, img2):

    if img1 is None or img2 is None:
        print("ERROR: image is None")
        return 0.0, 0.0

    try:

        # توحيد الحجم
        if img1.shape != img2.shape:
            img2 = cv2.resize(
                img2,
                (img1.shape[1], img1.shape[0])
            )

        # توحيد النوع
        img1 = np.clip(img1, 0, 255).astype(np.uint8)
        img2 = np.clip(img2, 0, 255).astype(np.uint8)

        psnr = metrics.calculate_psnr(img1, img2)
        ssim = metrics.calculate_ssim(img1, img2)

        if np.isinf(psnr) or np.isnan(psnr):
            psnr = 0.0

        if np.isnan(ssim):
            ssim = 0.0

        return psnr, ssim

    except Exception as e:

        print("SAFE METRICS ERROR:", e)

        return 0.0, 0.0



def prepare_text_bits(text):

    clean_text = embedding.arabic_preprocess(text)

    combined_text = embedding.encode_priority(clean_text)

    parts = combined_text.split("|||")

    if len(parts) != 3:
        raise ValueError("Text split error")

    template_str, important_text, normal_text = parts

    important_encrypted = encryption.encrypt_text(
        template_str + "|||" + important_text,
        PASSWORD
    )

    normal_encrypted = encryption.encrypt_text(
        normal_text,
        PASSWORD
    )

    important_bits = embedding.bytes_to_bits(important_encrypted)

    normal_bits = embedding.bytes_to_bits(normal_encrypted)

    return important_bits, normal_bits


def evaluate_single_image(image_path, text, compare_baseline=False):

    # تجهيز البتات
    important_bits, normal_bits = prepare_text_bits(text)

    original_bits = important_bits + normal_bits

    # فحص السعة
    capacity = embedding.calculate_capacity(image_path)

    total_bits = len(original_bits) + 64

    if total_bits > capacity["bits"]:
        return None

    # مسار الصورة
    stego_path = os.path.join(
        UPLOAD_FOLDER,
        f"stego_{os.path.basename(image_path)}"
    )

    # الإخفاء
    embedding.embed_semantic(
        image_path,
        important_bits,
        normal_bits,
        stego_path,
        PASSWORD
    )

    # قراءة الصور
    original_img = cv2.imread(image_path)
    stego_img = cv2.imread(stego_path)

    # حساب المقاييس
    psnr, ssim = safe_metrics(original_img, stego_img)

    extracted_bits = extraction.extract_semantic(
        stego_path,
        PASSWORD,
        return_bits=True
    )

    ber = metrics.calculate_ber(
        original_bits,
        extracted_bits
    )

    # =========================
    # SAS SECURITY METRICS
    # =========================

    chi_sas = security_metrics.histogram_attack_test(
        original_img,
        stego_img
    )

    rs_sas = security_metrics.rs_steganalysis(
        stego_img
    )

    _, stego_ent_sas, _ = security_metrics.entropy_analysis(
        original_img,
        stego_img
    )

    result = {
        "image": os.path.basename(image_path),

        "psnr_sas": float(round(psnr, 2)),
        "ssim_sas": float(round(ssim, 4)),
        "ber_sas": float(round(ber, 6)),

        "chi_sas": float(round(chi_sas, 2)),
        "rs_sas": float(round(rs_sas, 4)),
        "entropy_sas": float(round(stego_ent_sas, 4)),
    }

    # =========================
    # BASELINE (LSB)
    # =========================
    if compare_baseline:

        classical_stego = baseline.classical_lsb_embed(
            cv2.imread(image_path).copy(),
            original_bits
        )

        classical_bits = baseline.classical_lsb_extract(
            classical_stego
        )[:len(original_bits)]

        psnr_lsb = metrics.calculate_psnr(original_img, classical_stego)
        ssim_lsb = metrics.calculate_ssim(original_img, classical_stego)
        ber_lsb = metrics.calculate_ber(original_bits, classical_bits)

        chi_lsb = security_metrics.histogram_attack_test(
            original_img,
            classical_stego
        )

        rs_lsb = security_metrics.rs_steganalysis(classical_stego)

        _, stego_ent_lsb, _ = security_metrics.entropy_analysis(
            original_img,
            classical_stego
        )

        result.update({
            "psnr_lsb": float(round(psnr_lsb, 2)),
            "ssim_lsb": float(round(ssim_lsb, 4)),
            "ber_lsb": float(round(ber_lsb, 6)),
            "chi_lsb": float(round(chi_lsb, 2)),
            "rs_lsb": float(round(rs_lsb, 4)),
            "entropy_lsb": float(round(stego_ent_lsb, 4)),
        })

    # الهجمات
    attacks = robustness.apply_attacks(stego_img)

    attack_results = {}

    for attack_name, attack_img in attacks.items():

        attack_psnr, attack_ssim = safe_metrics(
            original_img,
            attack_img
        )

        temp_path = os.path.join(
            UPLOAD_FOLDER,
            f"{attack_name}.png"
        )

        cv2.imwrite(temp_path, attack_img)

        attack_bits = extraction.extract_semantic(
            temp_path,
            PASSWORD,
            return_bits=True
        )

        attack_ber = metrics.calculate_ber(
            original_bits,
            attack_bits
        )

        attack_results[attack_name] = {
            "psnr": float(round(attack_psnr, 2)),
            "ssim": float(round(attack_ssim, 4)),
            "ber": float(round(attack_ber, 6))
        }

    
    # النتائج
    result.update({

        "psnr_jpeg": attack_results["jpeg"]["psnr"],
        "ssim_jpeg": attack_results["jpeg"]["ssim"],
        "ber_jpeg": attack_results["jpeg"]["ber"],

        "psnr_noise": attack_results["noise"]["psnr"],
        "ssim_noise": attack_results["noise"]["ssim"],
        "ber_noise": attack_results["noise"]["ber"],

        "psnr_crop": attack_results["crop"]["psnr"],
        "ssim_crop": attack_results["crop"]["ssim"],
        "ber_crop": attack_results["crop"]["ber"],
    })

    return result


# =========================
# DATASET EVALUATION
# =========================

@app.route('/admin/admin_evaluate', methods=['POST'])
def admin_evaluate():

    dataset_folder = os.path.join("admin", "dataset")

    results = []

    for img_name in os.listdir(dataset_folder):

        # تجاهل الملفات غير الصور
        if not img_name.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.bmp')
        ):
            continue

        image_path = os.path.join(
            dataset_folder,
            img_name
        )

        try:

            result = evaluate_single_image(
                image_path,
                TEST_TEXT
            )

            if result:
                results.append(result)

            print("✅ Success:", img_name)

        except Exception as e:

            print("❌ FAILED:", img_name, str(e))

            continue

    return jsonify(results)


# =========================
# BASELINE COMPARISON
# =========================

def run_baseline_job():

    global evaluation_progress
    global cancel_requested

    cancel_requested = False

    dataset_folder = os.path.join("admin", "dataset")

    images = [
        f for f in os.listdir(dataset_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
    ]

    evaluation_progress["running"] = True
    evaluation_progress["finished"] = False
    evaluation_progress["progress"] = 0
    evaluation_progress["current"] = 0
    evaluation_progress["total"] = len(images)
    evaluation_progress["results"] = []

    for index, img_name in enumerate(images):

        if cancel_requested:

            print("⛔ Evaluation cancelled.")

            evaluation_progress["running"] = False
            evaluation_progress["finished"] = True

            break

        image_path = os.path.join(
            dataset_folder,
            img_name
        )

        try:

            result = evaluate_single_image(
                image_path,
                TEST_TEXT,
                compare_baseline=True
            )

            if result:
                evaluation_progress["results"].append(result)

        except Exception as e:

            print(e)

        evaluation_progress["current"] = index + 1

        evaluation_progress["progress"] = int(
            ((index + 1) / len(images)) * 100
        )

    evaluation_progress["running"] = False
    evaluation_progress["finished"] = True

@app.route('/admin/baseline_comparison', methods=['POST'])
def baseline_comparison():

    global evaluation_progress

    if evaluation_progress["running"]:

        return jsonify({
            "status":"running"
        })

    thread = threading.Thread(
        target=run_baseline_job
    )

    thread.start()

    return jsonify({
        "status":"started"
    })

# ---------------- RUN ----------------

@app.route('/admin/evaluation_progress')
def get_progress():

    return jsonify({

        "running":
            evaluation_progress["running"],

        "finished":
            evaluation_progress["finished"],

        "progress":
            evaluation_progress["progress"],

        "current":
            evaluation_progress["current"],

        "total":
            evaluation_progress["total"]

    })

@app.route('/admin/evaluation_results')
def evaluation_results():

    return jsonify({
        "images":
            evaluation_progress["results"]
    })

@app.route('/admin/cancel_evaluation', methods=['POST'])
def cancel_evaluation():

    global cancel_requested
    global evaluation_progress

    cancel_requested = True

    evaluation_progress["running"] = False
    evaluation_progress["finished"] = True

    return jsonify({
        "status": "cancelled"
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        threaded=True
    )