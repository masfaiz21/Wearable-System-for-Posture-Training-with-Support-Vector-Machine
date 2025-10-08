import pandas as pd
import os
import glob
import json 

def calculate_global_min_max_from_structured_data(base_data_directory):
    r"""
    Menghitung nilai minimum dan maksimum global untuk setiap dari 8 fitur mentah
    dengan membaca semua file CSV dari semua subjek dan kedua jenis gerakan.

    Args:
        base_data_directory (str): Direktori dasar tempat folder 'tesgerakanbenar' dan 'tesgerakansalah' berada.
                                   Contoh: r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable"
                                   >>> PERHATIKAN AWALAN 'r' di contoh path <<<
    
    Returns:
        dict: Dictionary berisi nilai min dan max global untuk setiap fitur,
              dalam format yang siap di-copy ke C++.
    """ 
    all_raw_data_frames = []
    
    # Definisi struktur folder dan awalan nama file CSV
    movement_categories = {
        "tesgerakanbenar": "repbenar", 
        "tesgerakansalah": "repsalah"  
    }

    # Kolom fitur mentah yang akan dihitung min-max-nya
    raw_features_to_analyze = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]

    print("Memulai pengumpulan data dari semua subjek dan gerakan...")

    for category_folder, csv_prefix in movement_categories.items():
        # Path ke direktori 'v4(skripsi)' atau 'v3(ambil gym)' di dalam setiap kategori
        version_dirs = glob.glob(os.path.join(base_data_directory, category_folder, 'v4(skripsi)'), recursive=False)
        
        if not version_dirs:
            print(f"Peringatan: Tidak ditemukan folder versi (misal v4(skripsi) atau v3(ambil gym)) di {os.path.join(base_data_directory, category_folder)}. Melewatkan {category_folder}.")
            continue
        
        actual_version_dir = version_dirs[0] # Ambil yang pertama ditemukan
        
        # --- Tambahan: Variabel untuk menghitung baris per subjek ---
        print(f"\nProcessing category: {category_folder}")
        
        for i in range(1, 16): # subjek1 hingga subjek15
            subject_folder = os.path.join(actual_version_dir, f"subjek{i}")
            subject_total_rows = 0 # Inisialisasi hitungan baris untuk subjek ini
            
            if not os.path.isdir(subject_folder):
                print(f"  Peringatan: Folder subjek{i} tidak ditemukan di {actual_version_dir}. Melanjutkan.")
                continue
            
            for j in range(1, 13): # repetisi 1 hingga 12
                csv_filename = f"{csv_prefix}{j}.csv"
                csv_filepath = os.path.join(subject_folder, csv_filename)
                
                if not os.path.exists(csv_filepath):
                    continue
                
                try:
                    df_temp = pd.read_csv(csv_filepath)
                    
                    df_temp_filtered = df_temp[raw_features_to_analyze]
                    all_raw_data_frames.append(df_temp_filtered)
                    subject_total_rows += len(df_temp_filtered) # Tambahkan ke hitungan subjek
                    
                except KeyError as ke:
                    print(f"  Error: Kolom fitur tidak lengkap di {csv_filepath}. Pesan: {ke}. Melanjutkan.")
                except Exception as e:
                    print(f"  Error saat membaca atau memproses {csv_filepath}: {e}. Melanjutkan.")
                    continue
            
            # --- Tambahan: Cetak baris data per subjek ---
            print(f"  {category_folder}/subjek{i}: {subject_total_rows} baris data mentah")
                    
    if not all_raw_data_frames:
        print("\nTidak ada file CSV mentah yang berhasil dikumpulkan untuk analisis min-max.")
        return {}

    combined_df = pd.concat(all_raw_data_frames, ignore_index=True)
    print(f"\nTotal {len(combined_df)} baris data mentah berhasil digabungkan dari semua file.")

    global_min_max_results = {}
    for feature in raw_features_to_analyze:
        if feature in combined_df.columns:
            min_val = combined_df[feature].min()
            max_val = combined_df[feature].max()
            global_min_max_results[feature] = {'min': float(min_val), 'max': float(max_val)}
        else:
            print(f"Peringatan: Fitur '{feature}' tidak ditemukan di DataFrame gabungan. Skip.")
            
    return global_min_max_results

# --- Konfigurasi Direktori Utama Dataset Anda ---
base_data_directory = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable"

if __name__ == "__main__":
    global_min_max_data = calculate_global_min_max_from_structured_data(base_data_directory)

    print("\n--- Hasil Perhitungan Nilai Min-Max Global ---")
    if global_min_max_data:
        print("GLOBAL_MIN_MAX = {")
        for feature, values in global_min_max_data.items():
            print(f"    '{feature}': {{'min': {values['min']:.6f}, 'max': {values['max']:.6f}}},")
        print("}")

        output_json_path = os.path.join(os.path.dirname(__file__), "global_min_max_values.json")
        with open(output_json_path, 'w') as f:
            json.dump(global_min_max_data, f, indent=4)
        print(f"\nNilai min-max global juga disimpan ke: {output_json_path}")
    else:
        print("Tidak ada nilai min-max yang dihasilkan. Pastikan path dan struktur folder sudah benar.")
    
    print("\n--- Proses Selesai ---")