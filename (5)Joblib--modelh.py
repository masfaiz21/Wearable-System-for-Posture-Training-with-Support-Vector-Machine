import joblib
import numpy as np
import os

# --- Konfigurasi ---
# Path ke direktori tempat model dan scaler .joblib Anda disimpan
MODEL_INPUT_DIRECTORY = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Trained_SVM_Model_Final"
MODEL_FILENAME = "svm_model_final.joblib"
SCALER_FILENAME = "scaler_final.joblib"

# Nama file .h output yang akan dibuat
OUTPUT_HEADER_FILE = "svm_model_params.h"

# --- Muat Model dan Scaler ---
print("Memuat model dan scaler...")
try:
    best_svm_model = joblib.load(os.path.join(MODEL_INPUT_DIRECTORY, MODEL_FILENAME))
    scaler = joblib.load(os.path.join(MODEL_INPUT_DIRECTORY, SCALER_FILENAME))
    print("Model dan Scaler berhasil dimuat.")
except FileNotFoundError as e:
    print(f"Error: File model atau scaler tidak ditemukan di '{MODEL_INPUT_DIRECTORY}'.")
    print("Pastikan Anda sudah menjalankan TrainSVM_GridSearch.py dan file-nya tersimpan.")
    exit()
except Exception as e:
    print(f"Error saat memuat model/scaler: {e}")
    exit()

# --- Ekstraksi Parameter Scaler ---
scaler_means = scaler.mean_
scaler_stds = scaler.scale_

# --- Ekstraksi Parameter SVM ---
# Parameter yang diekstrak tergantung pada jenis kernel
svm_kernel = best_svm_model.kernel
svm_bias = best_svm_model.intercept_[0] # Intercept biasanya array 1 elemen

# Untuk kernel RBF, kita butuh support vectors, dual_coef, dan gamma
# Untuk kernel Linear, kita butuh coef_ dan intercept_
svm_params_str = ""
if svm_kernel == 'linear':
    print(f"Model SVM menggunakan kernel: {svm_kernel}")
    svm_weights = best_svm_model.coef_[0] # Bobot untuk kelas 1 (SVC biner)
    
    svm_params_str += f"// SVM Model Parameters for LINEAR Kernel\n"
    svm_params_str += f"const float SVM_WEIGHTS[{len(svm_weights)}] = {{\n    "
    svm_params_str += ",    ".join(map(str, svm_weights))
    svm_params_str += "\n};\n"
    svm_params_str += f"const float SVM_BIAS = {svm_bias:.6f};\n"
    
elif svm_kernel == 'rbf':
    print(f"Model SVM menggunakan kernel: {svm_kernel}")
    # Support Vectors: array 2D
    support_vectors = best_svm_model.support_vectors_
    # Dual Coefficients: bobot untuk setiap support vector
    dual_coef = best_svm_model.dual_coef_[0] # Koefisien untuk kelas 1
    # Gamma: nilai gamma kernel RBF
    svm_gamma = best_svm_model.gamma
    
    # Peringatan jika jumlah support vectors terlalu banyak untuk ESP32
    if len(support_vectors) > 100: # Contoh ambang batas, sesuaikan
        print(f"Peringatan: Model RBF memiliki {len(support_vectors)} Support Vectors.")
        print("Ini mungkin terlalu banyak untuk memori ESP32.")
        print("Pertimbangkan untuk mencoba kernel 'linear' atau menyederhanakan model.")

    svm_params_str += f"// SVM Model Parameters for RBF Kernel\n"
    svm_params_str += f"const float SVM_GAMMA = {svm_gamma:.6f};\n"
    svm_params_str += f"const int NUM_SUPPORT_VECTORS = {len(support_vectors)};\n"
    
    svm_params_str += f"const float SUPPORT_VECTORS[{len(support_vectors)}][{len(support_vectors[0])}] = {{\n"
    for i, sv in enumerate(support_vectors):
        svm_params_str += "    {" + ", ".join(map(str, sv)) + "}"
        if i < len(support_vectors) - 1:
            svm_params_str += ",\n"
        else:
            svm_params_str += "\n"
    svm_params_str += "};\n"

    svm_params_str += f"const float DUAL_COEFS[{len(dual_coef)}] = {{\n    "
    svm_params_str += ",    ".join(map(str, dual_coef))
    svm_params_str += "\n};\n"
    svm_params_str += f"const float SVM_BIAS = {svm_bias:.6f};\n"

else:
    print(f"Kernel SVM '{svm_kernel}' tidak didukung untuk hardcoding ke C++ dalam skrip ini.")
    exit()

# --- Format untuk File Header .h ---
header_content = f"""
#ifndef SVM_MODEL_PARAMS_H
#define SVM_MODEL_PARAMS_H

// Auto-generated from Python script. Do NOT modify manually.

// --- StandardScaler Parameters ---
const float SCALER_MEANS[{len(scaler_means)}] = {{
    {',    '.join(map(str, scaler_means))}
}};

const float SCALER_STDS[{len(scaler_stds)}] = {{
    {',    '.join(map(str, scaler_stds))}
}};

{svm_params_str}

#endif // SVM_MODEL_PARAMS_H
"""

# --- Simpan ke File .h ---
output_filepath = os.path.join(MODEL_INPUT_DIRECTORY, OUTPUT_HEADER_FILE)
try:
    with open(output_filepath, 'w') as f:
        f.write(header_content)
    print(f"\nParameter model dan scaler berhasil diekstrak ke: {output_filepath}")
    print("Anda sekarang dapat menyertakan file ini (.h) ke proyek Arduino ESP32 Anda.")
except Exception as e:
    print(f"Error saat menyimpan file header: {e}")

print("\n--- Proses Hardcoding Selesai ---")