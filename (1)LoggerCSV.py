import serial
import csv
import time
import os
import sys

# --- Konfigurasi Serial ---
SERIAL_PORT = 'COM3'  # <<<< Ganti dengan port COM ESP32 IMU Transmitter Anda >>>>
BAUD_RATE = 115200

# --- Konfigurasi File CSV (DIPINDAHKAN KE SINI DAN DIATUR LANGSUNG) ---
# <<<< ATUR ALAMAT PENYIMPANAN DI SINI >>>>
OUTPUT_DIRECTORY = r"E:\College Stuff\New Environment Testv2\SKRIPSI LURR\Hasil Ambil Data Wearable\tesgerakanbenar\v4(skripsi)\subjek16"

# <<<< ATUR NAMA FILE CSV DI SINI >>>>
# Nama file akan menjadi "BASE_FILENAME.csv"
BASE_FILENAME = "repbenar16" 

# Header untuk file CSV (sesuai urutan output dari ESP32 IMU Transmitter)
CSV_HEADER = ["ax", "ay", "az", "gx", "gy", "gz", "mav", "rms"]

# --- Pastikan direktori output ada ---
# Skrip akan membuat direktori jika belum ada
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

def get_output_filepath():
    """Membangun path lengkap file output berdasarkan konfigurasi."""
    final_filename = f"{BASE_FILENAME}.csv"
    output_filepath = os.path.join(OUTPUT_DIRECTORY, final_filename)
    
    # Menambahkan timestamp jika file sudah ada untuk menghindari menimpa
    if os.path.exists(output_filepath):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        final_filename_with_timestamp = f"{BASE_FILENAME}_{timestamp}.csv"
        output_filepath = os.path.join(OUTPUT_DIRECTORY, final_filename_with_timestamp)
        print(f"Peringatan: File '{BASE_FILENAME}.csv' sudah ada.")
        print(f"Menyimpan data ke nama file baru: '{os.path.basename(output_filepath)}'")
            
    return output_filepath

def start_logging():
    """Memulai proses logging data dari serial ke CSV."""
    output_filepath = get_output_filepath() # Dapatkan path file dari fungsi

    # Inisialisasi Serial
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Terhubung ke ESP32 di {SERIAL_PORT}")
        time.sleep(2) # Beri waktu inisialisasi serial
        ser.flushInput() # Bersihkan buffer input serial
    except serial.SerialException as e:
        print(f"Error saat terhubung ke port serial: {e}")
        print("Pastikan port COM sudah benar dan ESP32 terhubung.")
        return

    # Mode 'w' untuk menulis (akan membuat file baru atau menimpa jika sudah ada)
    # newline='' untuk mencegah baris kosong tambahan
    with open(output_filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(CSV_HEADER) # Tulis header CSV

        print(f"Logging data ke {output_filepath}...")
        print("Data juga akan ditampilkan di konsol.")
        print("Tekan Ctrl+C untuk menghentikan logging kapan saja.")

        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    try:
                        # Pisahkan nilai-nilai berdasarkan koma
                        values = line.split(',')
                        
                        # Konversi ke float
                        numeric_values = [float(val) for val in values]

                        # Pastikan jumlah kolom sesuai (8 fitur)
                        if len(numeric_values) == len(CSV_HEADER):
                            csv_writer.writerow(numeric_values)
                            # Menampilkan data di konsol seperti serial monitor
                            print(line) 
                        else:
                            pass # Lewati baris yang salah format
                    except ValueError:
                        pass # Lewati baris dengan error parsing
                    except Exception as e:
                        print(f"Error memproses baris '{line}': {e}")
                
                # Tambahkan jeda kecil agar tidak terlalu membebani CPU
                time.sleep(0.001) 

        except KeyboardInterrupt:
            print("\nLogging dihentikan oleh pengguna (Ctrl+C).")
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga selama logging: {e}")
        finally:
            ser.close()
            print("Port serial ditutup.")
            print(f"Data berhasil disimpan ke {output_filepath}")

def main_menu():
    """Menampilkan menu utama kepada pengguna."""
    while True:
        print("\n--- Menu Logger Data Sensor ---")
        print("1. Mulai Logging Data (Tekan 'S')")
        print("2. Keluar (Tekan 'E')")
        
        choice = input("Pilih opsi: ").upper()
        
        if choice == 'S':
            start_logging()
        elif choice == 'E':
            print("Keluar dari program.")
            sys.exit()
        else:
            print("Pilihan tidak valid. Mohon masukkan 'S' atau 'E'.")

# Jalankan menu utama
if __name__ == "__main__":
    main_menu()