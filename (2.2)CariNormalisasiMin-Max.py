# import pandas as pd
# import os
# import json # Untuk menyimpan output dalam format JSON

# def calculate_min_max_from_single_csv(csv_filepath):
#     """
#     Membaca satu file CSV dan menghitung nilai minimum dan maksimum
#     untuk fitur-fitur yang ditentukan.

#     Args:
#         csv_filepath (str): Path lengkap ke file CSV yang akan dianalisis.

#     Returns:
#         dict: Dictionary berisi nilai min dan max global untuk setiap fitur,
#               dalam format yang siap di-copy ke C++.
#     """
    
#     # Pastikan file CSV ada
#     if not os.path.exists(csv_filepath):
#         print(f"Error: File CSV tidak ditemukan di {csv_filepath}")
#         return {}

#     # Membaca file CSV
#     try:
#         df = pd.read_csv(csv_filepath)
#         print(f"File '{os.path.basename(csv_filepath)}' berhasil dimuat. Total {len(df)} baris data.")
#     except Exception as e:
#         print(f"Error saat membaca file CSV {csv_filepath}: {e}")
#         return {}

#     # Fitur mentah yang akan dianalisis min-max-nya
#     raw_features_to_analyze = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]

#     global_min_max_results = {}
#     print("\n--- Hasil Perhitungan Nilai Min-Max Global ---")
#     print("GLOBAL_MIN_MAX = {")
    
#     for feature in raw_features_to_analyze:
#         if feature in df.columns:
#             min_val = df[feature].min()
#             max_val = df[feature].max()
#             global_min_max_results[feature] = {'min': float(min_val), 'max': float(max_val)}
#             print(f"    '{feature}': {{'min': {min_val:.6f}, 'max': {max_val:.6f}}},")
#         else:
#             print(f"Peringatan: Fitur '{feature}' tidak ditemukan di CSV. Skip.")
            
#     print("}")
    
#     return global_min_max_results

# if __name__ == "__main__":
#     # --- Konfigurasi ---
#     # Path lengkap ke file CSV gabungan yang sudah Anda miliki
#     combined_csv_path = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\all_raw_sensor_data_combined_from_v4.csv"
    
#     min_max_data = calculate_min_max_from_single_csv(combined_csv_path)

#     if min_max_data:
#         # Opsional: Simpan hasil min-max ke file JSON
#         output_json_path = os.path.join(os.path.dirname(__file__), "global_min_max_values_single_csv.json")
#         with open(output_json_path, 'w') as f:
#             json.dump(min_max_data, f, indent=4)
#         print(f"\nNilai min-max global juga disimpan ke: {output_json_path}")
#     else:
#         print("Tidak ada nilai min-max yang dihasilkan.")
    
#     print("\n--- Proses Selesai ---")


import pandas as pd
import numpy as np

def find_global_min_max_for_features(input_csv_paths, output_txt_path):
    """
    Menggabungkan beberapa file CSV, mencari nilai minimum dan maksimum
    untuk setiap kolom fitur (kecuali kolom 'label'), dan menyimpannya
    ke dalam file teks.

    Args:
        input_csv_paths (list): List path ke file CSV input (32 fitur + label).
        output_txt_path (str): Path lengkap untuk menyimpan file teks output berisi min-max.
    """
    all_data_frames = []

    for path in input_csv_paths:
        try:
            df = pd.read_csv(path)
            all_data_frames.append(df)
            print(f"Berhasil membaca {path}. Shape: {df.shape}")
        except FileNotFoundError:
            print(f"Error: File tidak ditemukan di {path}. Pastikan path benar.")
            return
        except Exception as e:
            print(f"Terjadi kesalahan saat membaca {path}: {e}")
            return

    if not all_data_frames:
        print("Tidak ada data yang berhasil dibaca dari file input.")
        return

    # Gabungkan semua DataFrame menjadi satu
    combined_df = pd.concat(all_data_frames, ignore_index=True)
    print(f"\nSemua file digabungkan. Total Shape: {combined_df.shape}")

    # Identifikasi kolom fitur (semua kolom kecuali 'label')
    feature_columns = [col for col in combined_df.columns if col != 'label']
    print(f"Fitur yang akan dihitung min-max-nya ({len(feature_columns)} kolom):")
    print(feature_columns)

    # Hitung nilai min dan max untuk setiap kolom fitur
    min_values = combined_df[feature_columns].min()
    max_values = combined_df[feature_columns].max()

    # Cetak ke konsol untuk verifikasi cepat
    print("\n--- Nilai Minimum Global per Fitur ---")
    print(min_values)
    print("\n--- Nilai Maksimum Global per Fitur ---")
    print(max_values)

    # Simpan hasil ke file teks
    try:
        with open(output_txt_path, 'w') as f:
            f.write("const float GLOBAL_MIN_MAX_FEATURES_MIN[32] = {\n  ")
            # Tulis nilai minimum
            for i, col in enumerate(feature_columns):
                f.write(f"{min_values[col]:.6f}")
                if i < len(feature_columns) - 1:
                    f.write(", ")
                if (i + 1) % 4 == 0 and i < len(feature_columns) - 1: # Untuk format rapi (4 nilai per baris)
                    f.write("\n  ")
            f.write("\n};\n\n")

            f.write("const float GLOBAL_MIN_MAX_FEATURES_MAX[32] = {\n  ")
            # Tulis nilai maksimum
            for i, col in enumerate(feature_columns):
                f.write(f"{max_values[col]:.6f}")
                if i < len(feature_columns) - 1:
                    f.write(", ")
                if (i + 1) % 4 == 0 and i < len(feature_columns) - 1: # Untuk format rapi (4 nilai per baris)
                    f.write("\n  ")
            f.write("\n};\n")
        print(f"\nNilai min-max global berhasil disimpan ke: {output_txt_path}")
        print("Anda dapat menyalin isi file ini ke svm_model_params.h Anda.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menulis ke file {output_txt_path}: {e}")

# --- Cara Penggunaan ---
# Ganti dengan path ke file CSV 32 fitur yang belum dinormalisasi
# Asumsi Anda punya final_dataset_benar.csv dan final_dataset_salah.csv
# di direktori E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_32_Features
input_csv_files = [
    'E:/College Stuff/New Environment Testv2/SKRIPSI LURR/Dataset_Final_32_Features/final_dataset_benar.csv',
    'E:/College Stuff/New Environment Testv2/SKRIPSI LURR/Dataset_Final_32_Features/final_dataset_salah.csv'
]

# Path untuk menyimpan hasil min-max
output_min_max_file = 'global_min_max_params.txt'

# Jalankan fungsi
find_global_min_max_for_features(input_csv_files, output_min_max_file)