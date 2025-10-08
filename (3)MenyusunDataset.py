# import pandas as pd
# import numpy as np
# import os

# # --- Global Min-Max Values for Normalization ---
# # Ini adalah nilai min-max global yang Anda dapatkan dari analisis sebelumnya.
# # Pastikan nilai ini sudah benar dan berasal dari seluruh dataset raw gabungan Anda.
# GLOBAL_MIN_MAX = {
#     'ax': {'min': -9.660000, 'max': 96.000000},
#     'ay': {'min': -8.630000, 'max': 10.630000},
#     'az': {'min': -8.450000, 'max': 8.160000},
#     'gx': {'min': -1.650000, 'max': 1.160000},
#     'gy': {'min': -1.690000, 'max': 1.570000},
#     'gz': {'min': -2.760000, 'max': 2.710000},
#     'mav': {'min': 0.000000, 'max': 1770.340000},
#     'rms': {'min': 0.000000, 'max': 1987.700000},
# }

# def normalize_min_max(df_raw, global_min_max_values):
#     """
#     Melakukan normalisasi Min-Max pada DataFrame raw data menggunakan nilai min-max global.
#     Rumus: X_norm = (X - X_min) / (X_max - X_min)
#     """
#     df_normalized = df_raw.copy() # Buat salinan agar tidak mengubah DataFrame asli
    
#     sensor_columns = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]
    
#     for col in sensor_columns:
#         if col in df_normalized.columns and col in global_min_max_values:
#             col_min = global_min_max_values[col]['min']
#             col_max = global_min_max_values[col]['max']
            
#             # Hindari pembagian dengan nol jika max == min
#             if col_max == col_min:
#                 df_normalized[col] = 0.0 # Set ke 0 jika tidak ada variasi
#             else:
#                 df_normalized[col] = (df_normalized[col] - col_min) / (col_max - col_min)
#         else:
#             print(f"Peringatan: Kolom '{col}' tidak ditemukan di DataFrame atau di GLOBAL_MIN_MAX. Normalisasi diabaikan untuk kolom ini.")
            
#     return df_normalized

# def extract_features_from_normalized_data(df_normalized):
#     """
#     Mengekstrak 32 fitur (mean, std, min, max untuk 8 kolom sensor) dari DataFrame data yang sudah dinormalisasi.
#     Diasumsikan df_normalized adalah satu repetisi (dari satu file CSV).
#     """
#     features = []
    
#     # Kolom sensor yang akan diekstrak fiturnya (sudah dinormalisasi)
#     sensor_columns = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]

#     for col in sensor_columns:
#         if col in df_normalized.columns and not df_normalized[col].empty:
#             data = df_normalized[col]
#             features.append(data.mean())
#             features.append(data.std(ddof=1)) # ddof=1 untuk standard deviation sampel
#             features.append(data.min())
#             features.append(data.max())
#         else:
#             # Jika kolom tidak ada atau kosong, tambahkan nilai 0 untuk menjaga konsistensi jumlah fitur
#             features.extend([0.0, 0.0, 0.0, 0.0]) # 4 fitur per kolom

#     # Buat dictionary dengan nama fitur yang sesuai
#     feature_names = []
#     for col in sensor_columns:
#         feature_names.extend([f"mean_{col}", f"std_{col}", f"min_{col}", f"max_{col}"])
    
#     return pd.Series(features, index=feature_names)

# def process_movement_type(base_dir, movement_folder_name, csv_prefix, global_min_max_values):
#     """
#     Memproses semua folder subjek dan file CSV untuk satu jenis gerakan (benar/salah).
#     Melakukan normalisasi, mengekstrak fitur, dan menggabungkannya ke dalam satu DataFrame.
#     """
#     all_features_data = [] 
    
#     movement_dir = os.path.join(base_dir, movement_folder_name, "v4(skripsi)")
    
#     for i in range(1, 16): # Asumsi dari subjek1 hingga subjek15
#         subject_folder = os.path.join(movement_dir, f"subjek{i}")
        
#         if not os.path.isdir(subject_folder):
#             print(f"Peringatan: Folder subjek{i} tidak ditemukan di {movement_dir}. Melanjutkan ke subjek berikutnya.")
#             continue
            
#         print(f"Memproses {movement_folder_name} untuk subjek{i}...")
        
#         for j in range(1, 13): # Asumsi dari repetisi 1 hingga 12
#             csv_filename = f"{csv_prefix}{j}.csv"
#             csv_filepath = os.path.join(subject_folder, csv_filename)
            
#             if not os.path.exists(csv_filepath):
#                 print(f"  Peringatan: File {csv_filename} tidak ditemukan di {subject_folder}. Melanjutkan.")
#                 continue
            
#             try:
#                 df_raw_repetition = pd.read_csv(csv_filepath)
                
#                 # --- LANGKAH BARU: Normalisasi Min-Max Data Mentah ---
#                 df_normalized_repetition = normalize_min_max(df_raw_repetition, global_min_max_values)
                
#                 # --- Ekstrak Fitur dari Data yang Sudah Dinormalisasi ---
#                 features_series = extract_features_from_normalized_data(df_normalized_repetition)
                
#                 all_features_data.append(features_series)
                
#             except Exception as e:
#                 print(f"  Error saat membaca atau memproses {csv_filepath}: {e}")
#                 continue
                
#     if all_features_data:
#         final_df = pd.DataFrame(all_features_data)
#         return final_df
#     else:
#         print(f"Tidak ada data yang berhasil diproses untuk {movement_folder_name}.")
#         return pd.DataFrame() 

# # --- Konfigurasi Direktori Utama ---
# base_data_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable"
# output_save_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_Normalized_Features"

# # Pastikan direktori output ada
# os.makedirs(output_save_directory, exist_ok=True)

# # --- Proses Gerakan Benar ---
# print("--- Memulai Proses Gerakan BENAR ---")
# df_benar_features = process_movement_type(base_data_directory, "tesgerakanbenar", "repbenar", GLOBAL_MIN_MAX)
# if not df_benar_features.empty:
#     df_benar_features['label'] = 1 
#     output_benar_path = os.path.join(output_save_directory, "final_dataset_benar_normalized.csv")
#     df_benar_features.to_csv(output_benar_path, index=False)
#     print(f"Dataset gerakan BENAR berhasil disimpan ke: {output_benar_path}")
#     print(f"Jumlah baris: {len(df_benar_features)}")
# else:
#     print("Tidak ada dataset gerakan BENAR yang dihasilkan.")

# # --- Proses Gerakan Salah ---
# print("\n--- Memulai Proses Gerakan SALAH ---")
# df_salah_features = process_movement_type(base_data_directory, "tesgerakansalah", "repsalah", GLOBAL_MIN_MAX)
# if not df_salah_features.empty:
#     df_salah_features['label'] = 0 
#     output_salah_path = os.path.join(output_save_directory, "final_dataset_salah_normalized.csv")
#     df_salah_features.to_csv(output_salah_path, index=False)
#     print(f"Dataset gerakan SALAH berhasil disimpan ke: {output_salah_path}")
#     print(f"Jumlah baris: {len(df_salah_features)}")
# else:
#     print("Tidak ada dataset gerakan SALAH yang dihasilkan.")

# print("\n--- Proses Selesai ---")


import pandas as pd
import numpy as np
import os

# --- GLOBAL MIN-MAX VALUES UNTUK 32 FITUR (dari perhitungan sebelumnya) ---
# Anda harus menyalin nilai ini persis dari output global_min_max_params.txt Anda
GLOBAL_MIN_MAX_FEATURES_MIN = np.array([
    2.705370, 1.565316, -9.660000, 8.140000,
    -0.707941, 2.264158, -8.630000, 8.210000,
    -4.870361, 0.224672, -8.450000, -3.680000,
    -0.136200, 0.048083, -1.650000, 0.030000,
    -0.048769, 0.068951, -1.690000, 0.150000,
    -0.117273, 0.341137, -2.760000, 0.630000,
    0.000000, 0.000000, 0.000000, 0.000000,
    0.000000, 0.000000, 0.000000, 0.000000
])

GLOBAL_MIN_MAX_FEATURES_MAX = np.array([
    8.650625, 13.621672, 5.020000, 96.000000,
    6.030175, 7.306840, 2.380000, 10.630000,
    2.322540, 5.181831, 0.640000, 8.160000,
    0.000652, 0.638653, -0.140000, 1.160000,
    0.108636, 0.469262, -0.060000, 1.570000,
    0.616154, 1.476777, -0.300000, 2.710000,
    1190.558571, 397.415504, 975.400000, 1770.340000,
    1410.400714, 472.594939, 1152.140000, 1987.700000
])

def normalize_dataset(input_csv_paths, output_directory):
    """
    Membaca file CSV yang berisi 32 fitur yang belum dinormalisasi,
    melakukan normalisasi Min-Max menggunakan nilai global,
    dan menyimpan hasilnya ke direktori output yang ditentukan.

    Args:
        input_csv_paths (list): List path lengkap ke file CSV input (32 fitur + label).
        output_directory (str): Path ke direktori tempat menyimpan file CSV hasil normalisasi.
    """
    # Buat direktori output jika belum ada
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Direktori '{output_directory}' dibuat.")

    # Nama kolom fitur (semua kecuali 'label')
    # Asumsi kolom-kolom ini ada di CSV 32 fitur Anda
    feature_columns_32 = [
        'mean_ax', 'std_ax', 'min_ax', 'max_ax',
        'mean_ay', 'std_ay', 'min_ay', 'max_ay',
        'mean_az', 'std_az', 'min_az', 'max_az',
        'mean_gx', 'std_gx', 'min_gx', 'max_gx',
        'mean_gy', 'std_gy', 'min_gy', 'max_gy',
        'mean_gz', 'std_gz', 'min_gz', 'max_gz',
        'mean_emg_mav', 'std_emg_mav', 'min_emg_mav', 'max_emg_mav',
        'mean_emg_rms', 'std_emg_rms', 'min_emg_rms', 'max_emg_rms'
    ]

    for input_path in input_csv_paths:
        try:
            df = pd.read_csv(input_path)
            print(f"Berhasil membaca {input_path}. Shape: {df.shape}")

            # Periksa apakah semua 32 kolom fitur yang diharapkan ada
            if not all(col in df.columns for col in feature_columns_32):
                missing_cols = [col for col in feature_columns_32 if col not in df.columns]
                print(f"Peringatan: Kolom fitur yang hilang di {input_path}: {missing_cols}")
                print("Lanjutkan dengan kolom yang ada. Pastikan urutan dan nama kolom sesuai dengan MIN/MAX global.")
                # Filter feature_columns_32 agar hanya mencakup kolom yang benar-benar ada di df
                actual_feature_columns = [col for col in feature_columns_32 if col in df.columns]
            else:
                actual_feature_columns = feature_columns_32

            # Lakukan normalisasi Min-Max
            df_normalized = df.copy() # Buat salinan untuk menghindari SettingWithCopyWarning

            for i, col in enumerate(actual_feature_columns):
                min_val = GLOBAL_MIN_MAX_FEATURES_MIN[i]
                max_val = GLOBAL_MIN_MAX_FEATURES_MAX[i]

                # Hitung rentang (max - min)
                data_range = max_val - min_val

                # Lakukan normalisasi. Hindari pembagian dengan nol jika min_val == max_val
                if data_range == 0:
                    df_normalized[col] = 0.0 # Jika range nol, set semua nilai menjadi 0
                else:
                    df_normalized[col] = (df[col] - min_val) / data_range
            
            # Ambil nama file dari path input
            file_name = os.path.basename(input_path)
            output_path = os.path.join(output_directory, file_name.replace('.csv', '_normalized.csv'))

            df_normalized.to_csv(output_path, index=False)
            print(f"Dataset dinormalisasi berhasil disimpan ke: {output_path}")
            print(f"Contoh 5 baris pertama hasil normalisasi {file_name}:")
            print(df_normalized.head())
            print(f"Shape hasil normalisasi {file_name}: {df_normalized.shape}\n")

        except FileNotFoundError:
            print(f"Error: File tidak ditemukan di {input_path}. Pastikan path benar.")
            continue
        except Exception as e:
            print(f"Terjadi kesalahan saat memproses {input_path}: {e}")
            continue

# --- Pengaturan Path ---
input_base_dir = r'E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_32_Features'
output_base_dir = r'E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_Normalized_32_Features'

input_csv_files = [
    os.path.join(input_base_dir, 'final_dataset_benar.csv'),
    os.path.join(input_base_dir, 'final_dataset_salah.csv')
]

# Jalankan fungsi normalisasi
normalize_dataset(input_csv_files, output_base_dir)