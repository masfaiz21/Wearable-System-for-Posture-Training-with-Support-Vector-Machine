# Wearable-System-for-Posture-Training-with-Support-Vector-Machine
Final project to complete my Engineering degree. Wearable System for Posture Training Triceps Extension that utilizes a combination of an Inertial Measurement Unit (IMU) MPU6050 sensor to detect forearm movements and a Muscle Sensor V3 (EMG) to measure triceps brachii muscle activity in the upper arm.

# Sistem Wearable untuk Klasifikasi Latihan Triceps Extension menggunakan SVM

Proyek ini merupakan sistem wearable yang dikembangkan sebagai bagian dari penyelesaian studi di Teknik Komputer. Sistem ini berfungsi untuk mengklasifikasikan gerakan latihan *Triceps Extension* sebagai "benar" atau "salah" secara *real-time* menggunakan sensor dan model _machine learning_ yang tertanam (_embedded_).

Sistem ini memanfaatkan kombinasi dua sensor utama:
* **Inertial Measurement Unit (IMU) MPU6050**: Untuk mendeteksi perubahan percepatan sudut pada gerakan lengan bawah.
* **Muscle Sensor V3 (EMG)**: Untuk mengukur impuls aktivitas otot *triceps brachii*.

Model klasifikasi yang digunakan adalah **Support Vector Machine (SVM)** yang telah dilatih dan di-deploy langsung ke mikrokontroler ESP32.

## Arsitektur Sistem

Sistem ini terdiri dari dua unit ESP32 yang berkomunikasi secara nirkabel menggunakan protokol **ESP-NOW**.

* **Unit Transmitter (Pergelangan Tangan)**:
    * Terhubung dengan sensor IMU MPU6050.
    * Membaca data akselerometer (`ax, ay, az`) dan giroskop (`gx, gy, gz`).
    * Memiliki tombol untuk memulai sekuens pembacaan data.
    * Mengirimkan data IMU ke Unit Receiver.

* **Unit Receiver (Punggung)**:
    * Terhubung dengan Muscle Sensor V3 (EMG).
    * Membaca data aktivitas otot dalam bentuk MAV (_Mean Absolute Value_) dan RMS (_Root Mean Square_).
    * Menerima data dari Unit Transmitter.
    * Menjalankan model SVM yang sudah tertanam untuk melakukan klasifikasi gerakan.
    * Terhubung ke PC/Laptop selama tahap pengambilan dataset.
 
## Alur Kerja Proyek

Proses pengembangan proyek ini dibagi menjadi empat tahap utama:

### 1. Pengambilan Dataset

Tahap ini bertujuan untuk mengumpulkan data mentah dari kedua sensor untuk digunakan dalam pelatihan model.

* **Perangkat Keras**:
    * Kode `KodeIMUtransmitterAmbilDataset.txt` diunggah ke ESP32 Transmitter.
    * Kode `KodeEMGreceiverAmbilDataset.txt` diunggah ke ESP32 Receiver.
    * ESP32 Receiver dihubungkan ke PC/Laptop melalui USB.
* **Perangkat Lunak**:
    * Skrip Python `(1)LoggerCSV.py` dijalankan di PC untuk membaca data serial dari ESP32 Receiver.
    * Data dari 6 fitur IMU (`ax, ay, az, gx, gy, gz`) dan 2 fitur EMG (`mav, rms`) disimpan dalam format `.csv`.
* **Proses**:
    * Data dikumpulkan dari 15 subjek yang melakukan gerakan benar dan salah.
    * Setiap subjek melakukan 12 repetisi, menghasilkan total 360 file `.csv` (180 data benar, 180 data salah).

### 2. Normalisasi & Pra-pemrosesan Data

Data mentah yang telah dikumpulkan kemudian diproses untuk mengekstraksi fitur yang lebih informatif dan dinormalisasi agar siap digunakan untuk melatih model.

1.  **Penggabungan Data**: 360 file `.csv` digabungkan menjadi satu dataset besar menggunakan skrip `(2.1)GabungCSV.py`.
2.  **Ekstraksi Fitur Tambahan**: Dari 8 fitur awal, diekstraksi 4 metrik statistik (`mean`, `std`, `min`, `max`) untuk masing-masing fitur. Ini menghasilkan total **32 fitur** yang lebih deskriptif. Proses ini dilakukan dengan skrip `(3.1)MenyusunDataset.py`.
3.  **Kalkulasi Parameter Normalisasi**: Skrip `(2.2)CariNormalisasiMin-Max.py` dijalankan untuk menghitung nilai minimum dan maksimum global dari 32 fitur sebagai parameter normalisasi.
4.  **Normalisasi**: Nilai min-max yang didapat di-hardcode ke dalam skrip `(3)MenyusunDataset.py` untuk menormalisasi dataset 32 fitur. Hasil akhirnya adalah sebuah file `.csv` yang siap untuk dilatih.

### 3. Pelatihan Model (Training)

Dataset yang telah bersih dan ternormalisasi digunakan untuk melatih model SVM.

1.  **Pelatihan**: Skrip `(4)TrainingSVM.py` dijalankan untuk melatih model SVM dan scaler menggunakan dataset yang telah disiapkan.
2.  **Hasil**: Proses ini menghasilkan dua file: `model.joblib` (model SVM yang terlatih) dan `scaler.joblib` (scaler untuk normalisasi).
3.  **Konversi Model**: Model `joblib` dikonversi menjadi format header C (`.h`) menggunakan skrip `(5)Joblib---modelh.py` agar dapat di-hardcode dan digunakan di dalam lingkungan Arduino/ESP32.

### 4. Deployment ke Perangkat

Model yang telah dikonversi di-deploy ke ESP32 Receiver untuk inferensi secara *on-device*.

* **Aplikasi**: Arduino IDE digunakan untuk mengunggah kode ke ESP32.
* **Kode**:
    * `KodeIMUtransmitterDeploy(Skripsi)v2.txt`: Diunggah ke ESP32 Transmitter.
    * `KodeEMGreceiverDeploy(Skripsi)v2.txt`: Diunggah ke ESP32 Receiver. Kode ini sudah berisi model SVM dalam format `.h`.

## Cara Kerja Sistem Final

1.  Subjek mengenakan kedua unit wearable: unit IMU di pergelangan tangan dan unit EMG di punggung (dekat otot triceps).
2.  Subjek menekan tombol pada unit di pergelangan tangan untuk memulai sekuens deteksi.
3.  Selama sekuens, perangkat akan:
    * Membaca beberapa frame data dari sensor IMU dan EMG.
    * Menghitung 32 fitur turunan (`mean`, `std`, `min`, `max`) dari data mentah.
    * Melakukan normalisasi pada 32 fitur tersebut.
    * Memasukkan data yang telah diproses ke dalam model SVM untuk klasifikasi.
4.  Hasil klasifikasi ("Benar" atau "Salah") dapat digunakan untuk memberikan umpan balik kepada pengguna (melalui buzzer).
