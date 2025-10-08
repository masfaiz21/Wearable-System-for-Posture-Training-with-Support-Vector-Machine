import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# --- Tambahan: Import untuk Plotting ---
import matplotlib.pyplot as plt
import seaborn as sns

# --- Konfigurasi Direktori Dataset ---
DATASET_DIRECTORY = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Dataset_Final_Normalized_32_Features"

# Nama file dataset yang sudah diproses dan dinormalisasi
BENAR_DATASET_FILENAME = "final_dataset_benar_normalized.csv"
SALAH_DATASET_FILENAME = "final_dataset_salah_normalized.csv"

# --- Konfigurasi Output Model ---
MODEL_OUTPUT_DIRECTORY = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Trained_SVM_Model_Final" # Ganti nama folder output jika perlu
MODEL_FILENAME = "svm_model_final.joblib"
SCALER_FILENAME = "scaler_final.joblib"
# Nama file untuk plot Confusion Matrix
CONFUSION_MATRIX_PLOT_FILENAME = "confusion_matrix_32_svm.png"

# Pastikan direktori output model ada
os.makedirs(MODEL_OUTPUT_DIRECTORY, exist_ok=True)


def run_svm_training(benar_filename, salah_filename, scenario_name, output_dir):
    """
    Fungsi untuk menjalankan proses training SVM pada dataset tertentu.
    """
    print(f"\n=== Menjalankan Training untuk Skenario: {scenario_name} ===")
    
    # Muat Dataset
    print(f"Memuat dataset: {benar_filename} dan {salah_filename}...")
    try:
        df_benar = pd.read_csv(os.path.join(DATASET_DIRECTORY, benar_filename))
        df_salah = pd.read_csv(os.path.join(DATASET_DIRECTORY, salah_filename))
        
        # Gabungkan kedua dataset
        df_combined = pd.concat([df_benar, df_salah], ignore_index=True)
        print(f"Total {len(df_combined)} baris data berhasil dimuat.")
        
    except FileNotFoundError as e:
        print(f"Error: Dataset tidak ditemukan. Pastikan file ada di '{DATASET_DIRECTORY}'.")
        return
    except Exception as e:
        print(f"Error saat memuat atau menggabungkan dataset: {e}")
        return

    # Pisahkan Fitur (X) dan Label (y)
    X = df_combined.drop('label', axis=1)
    y = df_combined['label']

    print(f"Jumlah fitur yang digunakan: {X.shape[1]} (tidak termasuk kolom 'label')")
    
    # Jumlah fitur yang diharapkan (32 sensor features + 1 duration_frames = 33)
    # ATAU 32 fitur sensor saja jika itu yang Anda gunakan terakhir untuk training
    # Berdasarkan hasil training terakhir Anda 32 fitur adalah akurat.
    expected_features = 32 

    if X.shape[1] != expected_features:
        print(f"Peringatan: Jumlah fitur yang ditemukan ({X.shape[1]}) tidak sesuai dengan yang diharapkan ({expected_features}).")


    # Bagi Data menjadi Training dan Testing Set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Ukuran data training: {len(X_train)} baris")
    print(f"Ukuran data testing: {len(X_test)} baris")

    # Standardisasi Fitur
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("Fitur berhasil distandardisasi (StandardScaler).")

    # Konfigurasi GridSearchCV untuk SVM
    # Menggunakan parameter yang terakhir memberikan akurasi 95.83%
    # Atau jika Anda ingin coba kernel linear yang 100%
    param_grid = [
        { # Ini adalah setting yang menghasilkan 95.83%
            'C': [0.0001, 0.001, 0.01],      
            'gamma': [0.0001, 0.001, 0.01],   
            'kernel': ['rbf']                 
        },
        # { # Optional: Coba juga kernel linear yang menghasilkan 100% akurasi
        #     'C': [0.0001, 0.001, 0.01, 0.1],      
        #     'kernel': ['linear']              
        # }
    ]

    svm = SVC(random_state=42, probability=True) 
    grid_search = GridSearchCV(svm, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=0) 

    print("Memulai pencarian parameter terbaik dengan GridSearchCV...")
    grid_search.fit(X_train_scaled, y_train)

    # Tampilkan Hasil GridSearchCV
    print("\n--- Hasil GridSearchCV ---")
    print(f"Parameter terbaik: {grid_search.best_params_}")
    print(f"Skor akurasi training terbaik (Cross-Validation): {grid_search.best_score_:.4f}")

    # Evaluasi Model Terbaik pada Data Testing
    best_svm_model = grid_search.best_estimator_ 
    y_pred = best_svm_model.predict(X_test_scaled)

    print("\n--- Evaluasi Model Terbaik pada Data Testing ---")

    # Akurasi
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Akurasi model pada data testing: {accuracy:.4f}")

    # Confusion Matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(conf_matrix)

    # Laporan Klasifikasi
    class_report = classification_report(y_test, y_pred, target_names=['Gerakan Salah (0)', 'Gerakan Benar (1)'])
    print("\nLaporan Klasifikasi:")
    print(class_report)

    # --- Tambahan: Membuat dan Menyimpan Plot Confusion Matrix ---
    plt.figure(figsize=(8, 6)) # Ukuran plot
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Prediksi Salah', 'Prediksi Benar'], 
                yticklabels=['Aktual Salah', 'Aktual Benar'])
    plt.title(f'Confusion Matrix: {scenario_name}\nAccuracy: {accuracy:.4f}')
    plt.ylabel('Aktual Label')
    plt.xlabel('Prediksi Label')
    
    plot_save_path = os.path.join(output_dir, CONFUSION_MATRIX_PLOT_FILENAME)
    plt.savefig(plot_save_path) # Simpan plot sebagai file gambar
    print(f"\nPlot Confusion Matrix disimpan ke: {plot_save_path}")
    # plt.show() # Tampilkan plot di layar (aktifkan jika Anda menjalankan di lingkungan interaktif seperti Spyder atau Jupyter)

    # Simpan Model dan Scaler
    model_save_path = os.path.join(output_dir, MODEL_FILENAME)
    scaler_save_path = os.path.join(output_dir, SCALER_FILENAME)

    joblib.dump(best_svm_model, model_save_path)
    joblib.dump(scaler, scaler_save_path) 

    print(f"\nModel SVM terbaik berhasil disimpan ke: {model_save_path}")
    print(f"Scaler berhasil disimpan ke: {scaler_save_path}")


# --- Jalankan Percobaan ---

# Skenario yang akan dijalankan
# Untuk mendapatkan plot confusion matrix dari model RBF 95.83%:
run_svm_training("final_dataset_benar_normalized.csv", "final_dataset_salah_normalized.csv", "Normalized_RBF", MODEL_OUTPUT_DIRECTORY)

# Jika Anda ingin menyimpan model linear 100% dan plotnya, jalankan ini saja:
# run_svm_training("final_dataset_benar_normalized.csv", "final_dataset_salah_normalized.csv", "Normalized_Linear_100_percent", MODEL_OUTPUT_DIRECTORY)

print("\n=== Semua Percobaan Selesai ===")