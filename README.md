

## data
Observasi pada data dilakukan selama **4.140 menit** (6 - 9 Maret 2020) melibatkan 5 sensor kelembaban tanah yang diletakkan pada titik berbeda[cite: 4, 6]. Proyek ini mencakup tahap pengambilan data,data cleaning, hingga visualisasi.

### Fitur Dashboard:
**Real-time Metrics:** Menampilkan nilai kelembaban terkini, minimum, dan maksimum untuk setiap sensor.
**Trend Analysis:** Grafik deret waktu (*Line Chart*) untuk melihat pola penguapan air.
**Spatial Heatmap:** Analisis rata-rata kelembaban per jam dan per hari untuk melihat pola kekeringan lahan[cite: 41].
**Distribution Analysis:** Menggunakan *Box Plot* dan *Histogram* untuk memahami karakteristik sebaran data di setiap titik sensor.

##  Teknologi yang Digunakan
**Bahasa Pemrograman:** Python 
**Library Analisis:** Pandas, NumPy
**Visualisasi:** Plotly, Matplotlib, Seaborn 
**Web Framework:** Streamlit 
**Deployment:** Streamlit Community Cloud 

## Metodologi Data Cleaning
Proyek ini menerapkan **Manual Thresholding** untuk menangani *outliers*. Berdasarkan *Domain Knowledge* sistem IoT, data dipertahankan dalam rentang fungsional **0.0 - 1.0**. 
