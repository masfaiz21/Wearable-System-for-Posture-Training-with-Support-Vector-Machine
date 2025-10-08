import pandas as pd
import numpy as np
import os

def extract_features_from_raw_data(df_raw):
    """
    Mengekstrak 32 fitur (mean, std, min, max untuk 8 kolom sensor) dari DataFrame raw data.
    Diasumsikan df_raw adalah satu repetisi (dari satu file CSV).
    """
    features = []
    
    # Kolom sensor yang akan diekstrak fiturnya
    sensor_columns = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]

    for col in sensor_columns:
        if col in df_raw.columns and not df_raw[col].empty:
            data = df_raw[col]
            features.append(data.mean())
            features.append(data.std(ddof=1)) # ddof=1 untuk standard deviation sampel
            features.append(data.min())
            features.append(data.max())
        else:
            # Jika kolom tidak ada atau kosong, tambahkan nilai 0 untuk menjaga konsistensi jumlah fitur
            features.extend([0.0, 0.0, 0.0, 0.0]) # 4 fitur per kolom

    # Buat dictionary dengan nama fitur yang sesuai
    feature_names = []
    for col in sensor_columns:
        feature_names.extend([f"mean_{col}", f"std_{col}", f"min_{col}", f"max_{col}"])
    
    return pd.Series(features, index=feature_names)

def process_movement_type(base_dir, movement_folder_name, csv_prefix): # <<<< MODIFIKASI: Tambah csv_prefix
    """
    Memproses semua folder subjek dan file CSV untuk satu jenis gerakan (benar/salah).
    Mengekstrak fitur dan menggabungkannya ke dalam satu DataFrame.
    """
    all_features_data = [] # List untuk menyimpan Series fitur dari setiap repetisi
    
    # Path ke direktori jenis gerakan (misal: "tesgerakanbenar/v3(ambil gym)")
    movement_dir = os.path.join(base_dir, movement_folder_name, "v4(skripsi)") # <<<< MODIFIKASI: Gunakan movement_folder_name
    
    # Iterasi melalui folder subjek (subjek1, subjek2, ...)
    for i in range(1, 16): # Asumsi dari subjek1 hingga subjek15
        subject_folder = os.path.join(movement_dir, f"subjek{i}")
        
        if not os.path.isdir(subject_folder):
            print(f"Peringatan: Folder subjek{i} tidak ditemukan di {movement_dir}. Melanjutkan ke subjek berikutnya.")
            continue
            
        print(f"Memproses {movement_folder_name} untuk subjek{i}...") # <<<< MODIFIKASI: Gunakan movement_folder_name
        
        # Iterasi melalui file CSV repetisi (repbenar1.csv, repbenar2.csv, ...)
        for j in range(1, 13): # Asumsi dari repetisi 1 hingga 12
            # --- BARIS INI YANG DIPERBAIKI ---
            csv_filename = f"{csv_prefix}{j}.csv" # <<<< MODIFIKASI: Gunakan csv_prefix >>>
            # Contoh: jika csv_prefix="repbenar", akan menjadi "repbenar1.csv"
            csv_filepath = os.path.join(subject_folder, csv_filename)
            
            if not os.path.exists(csv_filepath):
                print(f"  Peringatan: File {csv_filename} tidak ditemukan di {subject_folder}. Melanjutkan.")
                continue
            
            try:
                df_raw_repetition = pd.read_csv(csv_filepath)
                
                # Ekstrak fitur dari file CSV repetisi ini
                features_series = extract_features_from_raw_data(df_raw_repetition)
                
                all_features_data.append(features_series)
                
            except Exception as e:
                print(f"  Error saat membaca atau memproses {csv_filepath}: {e}")
                continue
                
    # Gabungkan semua Series fitur ke dalam satu DataFrame
    if all_features_data:
        final_df = pd.DataFrame(all_features_data)
        return final_df
    else:
        print(f"Tidak ada data yang berhasil diproses untuk {movement_folder_name}.") # <<<< MODIFIKASI
        return pd.DataFrame() # Kembalikan DataFrame kosong jika tidak ada data

# --- Konfigurasi Direktori Utama ---
base_data_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable"
output_save_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_32_Features"

# Pastikan direktori output ada
os.makedirs(output_save_directory, exist_ok=True)

# --- Proses Gerakan Benar ---
print("--- Memulai Proses Gerakan BENAR ---")
# <<<< MODIFIKASI: Tambahkan argumen movement_folder_name dan csv_prefix >>>
df_benar_features = process_movement_type(base_data_directory, "tesgerakanbenar", "repbenar") 
if not df_benar_features.empty:
    df_benar_features['label'] = 1 # Tambahkan kolom label untuk gerakan benar
    output_benar_path = os.path.join(output_save_directory, "final_dataset_benar.csv")
    df_benar_features.to_csv(output_benar_path, index=False)
    print(f"Dataset gerakan BENAR berhasil disimpan ke: {output_benar_path}")
    print(f"Jumlah baris: {len(df_benar_features)}")
else:
    print("Tidak ada dataset gerakan BENAR yang dihasilkan.")

# --- Proses Gerakan Salah ---
print("\n--- Memulai Proses Gerakan SALAH ---")
# <<<< MODIFIKASI: Tambahkan argumen movement_folder_name dan csv_prefix >>>
df_salah_features = process_movement_type(base_data_directory, "tesgerakansalah", "repsalah")
if not df_salah_features.empty:
    df_salah_features['label'] = 0 # Tambahkan kolom label untuk gerakan salah
    output_salah_path = os.path.join(output_save_directory, "final_dataset_salah.csv")
    df_salah_features.to_csv(output_salah_path, index=False)
    print(f"Dataset gerakan SALAH berhasil disimpan ke: {output_salah_path}")
    print(f"Jumlah baris: {len(df_salah_features)}")
else:
    print("Tidak ada dataset gerakan SALAH yang dihasilkan.")

print("\n--- Proses Selesai ---")


# import pandas as pd
# import numpy as np
# import os

# # --- Global Min-Max Values for Normalization ---
# # Ini adalah nilai min-max global yang Anda dapatkan dari analisis sebelumnya.
# # Pastikan nilai ini sudah benar dan berasal dari seluruh dataset raw gabungan Anda.
# GLOBAL_MIN_MAX = {
#     'ax': {'min': -16.660000, 'max': 14.530000},
#     'ay': {'min': -4.560000, 'max': 15.200000},
#     'az': {'min': -4.410000, 'max': 12.380000},
#     'gx': {'min': -2.470000, 'max': 1.990000},
#     'gy': {'min': -5.410000, 'max': 5.970000},
#     'gz': {'min': -4.290000, 'max': 4.600000},
#     'mav': {'min': 0.000000, 'max': 2153.750000},
#     'rms': {'min': 0.000000, 'max': 2424.500000}
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
    
#     movement_dir = os.path.join(base_dir, movement_folder_name, "v3(ambil gym)")
    
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