import pandas as pd
import glob
import os

# --- Konfigurasi Direktori Utama ---
# Ini adalah direktori yang berisi 'tesgerakanbenar' dan 'tesgerakansalah'
base_data_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable"

# Daftar folder kategori gerakan dan sub-path di dalamnya
# 'v4(skripsi)' adalah folder yang berisi subjek1-15
movement_paths = {
    "tesgerakanbenar": "v4(skripsi)",
    "tesgerakansalah": "v4(skripsi)"
}

# Nama file CSV output gabungan
output_combined_filename = "all_raw_sensor_data_combined_from_v4.csv"

# List untuk menyimpan semua DataFrame dari semua file CSV
all_dfs_to_combine = []

print("Memulai penggabungan semua file CSV dari semua subjek dan gerakan...")

# Iterasi melalui setiap kategori gerakan
for category_folder, version_subfolder in movement_paths.items():
    # Path lengkap ke direktori versi (misal: E:\...\tesgerakanbenar\v4(skripsi))
    current_version_path = os.path.join(base_data_directory, category_folder, version_subfolder)
    
    if not os.path.isdir(current_version_path):
        print(f"Peringatan: Direktori '{current_version_path}' tidak ditemukan. Melewatkan kategori ini.")
        continue

    print(f"\nMemproses kategori: {category_folder} di {current_version_path}")
    
    # Temukan semua folder 'subjekX' di dalam direktori versi
    # Menggunakan 'subjek*' untuk mencocokkan 'subjek1', 'subjek2', dst.
    subject_folders = glob.glob(os.path.join(current_version_path, "subjek*"))
    
    if not subject_folders:
        print(f"  Peringatan: Tidak ditemukan folder subjek di '{current_version_path}'.")
        continue

    # Urutkan folder subjek agar urutan pembacaan konsisten (misal: subjek1, subjek2, ...)
    subject_folders.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x)))))

    for subject_folder in subject_folders:
        subject_name = os.path.basename(subject_folder) # Mendapatkan nama folder subjek (misal 'subjek1')
        
        # Temukan semua file CSV di dalam folder subjek ini
        # "*.csv" akan mencocokkan "repbenarX.csv" atau "repsalahX.csv"
        csv_files_in_subject = glob.glob(os.path.join(subject_folder, "*.csv"))
        
        if not csv_files_in_subject:
            print(f"  Peringatan: Tidak ditemukan file CSV di '{subject_folder}'.")
            continue
            
        # Optional: Urutkan file CSV jika ingin konsisten (rep1, rep2, ...)
        csv_files_in_subject.sort() 
        
        # print(f"  Membaca dari {subject_name} ({len(csv_files_in_subject)} files)...")

        for file_path in csv_files_in_subject:
            try:
                df = pd.read_csv(file_path)
                
                # Opsional: Jika Anda ingin menambahkan kolom untuk identifikasi sumber data (subjek, rep, kategori)
                # df['subject_id'] = int(''.join(filter(str.isdigit, subject_name)))
                # df['repetition_id'] = int(''.join(filter(str.isdigit, os.path.basename(file_path).replace('.csv', ''))))
                # df['movement_category'] = category_folder

                all_dfs_to_combine.append(df)
            except Exception as e:
                print(f"  Error saat membaca file {file_path}: {e}")

if not all_dfs_to_combine:
    print("\nTidak ada data yang berhasil digabungkan. Periksa path dan struktur folder.")
else:
    # Gabungkan semua DataFrame menjadi satu DataFrame besar
    combined_master_df = pd.concat(all_dfs_to_combine, ignore_index=True)

    # Tentukan path output untuk file gabungan
    # Akan disimpan di direktori yang sama dengan skrip ini
    output_filepath = os.path.join(os.path.dirname(__file__), output_combined_filename)
    
    # Simpan ke CSV baru
    combined_master_df.to_csv(output_filepath, index=False)

    print(f"\nPenggabungan selesai. Total {len(combined_master_df)} baris data.")
    print(f"File gabungan disimpan di: {output_filepath}")
    
    # --- Tambahan: Hitung Min-Max Global dari Data Gabungan Ini ---
    print("\n--- Nilai Minimum dan Maksimum Global dari Data Mentah Gabungan ---")
    raw_features_to_analyze = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]
    
    global_min_max_results = {}
    print("GLOBAL_MIN_MAX = {")
    for feature in raw_features_to_analyze:
        if feature in combined_master_df.columns:
            min_val = combined_master_df[feature].min()
            max_val = combined_master_df[feature].max()
            global_min_max_results[feature] = {'min': float(min_val), 'max': float(max_val)}
            print(f"    '{feature}': {{'min': {values['min']:.6f}, 'max': {values['max']:.6f}}},")
        else:
            print(f"Peringatan: Fitur '{feature}' tidak ditemukan di DataFrame gabungan.")
    print("}")
    
    # Opsional: Simpan min-max ke file JSON
    # import json
    # output_json_path = os.path.join(os.path.dirname(__file__), "global_min_max_values_from_combined.json")
    # with open(output_json_path, 'w') as f:
    #     json.dump(global_min_max_results, f, indent=4)
    # print(f"\nNilai min-max global juga disimpan ke: {output_json_path}")

print("\n--- Proses Selesai ---")