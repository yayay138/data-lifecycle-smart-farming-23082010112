import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Laporan Analisis Data Sensor", layout="wide")

# 2. Sidebar 
with st.sidebar:
    st.write("Nama: M. Andaru Abyan")
    st.write("NIM: 23082010112")
    st.markdown("---")
    
    # Memuat data untuk mendapatkan rentang waktu awal
    data_path = 'outputs/cleaned_data.csv'
    if os.path.exists(data_path):
        df_init = pd.read_csv(data_path)
        df_init['timestamp'] = pd.to_datetime(df_init['timestamp'])
        
        st.write("**Filter Analisis**")
        min_date = df_init['timestamp'].min().to_pydatetime()
        max_date = df_init['timestamp'].max().to_pydatetime()
        
        # Slider 
        selected_range = st.slider(
            "Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="DD/MM/YY HH:mm"
        )
   

# 3. Eksekusi Dashboard Utama
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    sensor_cols = ['moisture0', 'moisture1', 'moisture2', 'moisture3', 'moisture4']
    
    #Memfilter data berdasarkan pilihan di sidebar
    mask = (df['timestamp'] >= selected_range[0]) & (df['timestamp'] <= selected_range[1])
    df_filtered = df.loc[mask]

    st.title("Laporan Analisis Kelembaban Tanah")
    st.write(f"Menampilkan {len(df_filtered)} baris data dari periode terpilih.")

    st.markdown("---")

    #Distribusi dan Rekapitulasi
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Visualisasi 1: Distribusi Nilai Sensor")
        df_melted = df_filtered.melt(id_vars=['timestamp'], value_vars=sensor_cols, var_name='Sensor', value_name='Nilai')
        fig_box = px.box(df_melted, x='Sensor', y='Nilai', color='Sensor')
        st.plotly_chart(fig_box, use_container_width=True)
        st.write("Keterangan: Merangkum rentang nilai minimum, median, dan maksimum setiap sensor pada periode terpilih.")

    with col2:
        st.subheader("Visualisasi 2: Rekapitulasi Aktivitas Irigasi")
        irrigation_counts = df_filtered['irrgation'].value_counts().reset_index()
        irrigation_counts.columns = ['Status', 'Jumlah']
        irrigation_counts['Status'] = irrigation_counts['Status'].map({True: 'Sistem Aktif', False: 'Sistem Mati'})
        
        fig_pie = px.pie(irrigation_counts, values='Jumlah', names='Status', hole=0.5,
                         color_discrete_map={'Sistem Aktif':'#2ca02c', 'Sistem Mati':'#d62728'})
        st.plotly_chart(fig_pie, use_container_width=True)
        st.write("Indikator: Hijau (Durasi sistem aktif), Merah (Durasi sistem mati).")

    st.markdown("---")

    #Tren dan Komparasi 
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Visualisasi 3: Tren Kumulatif Kelembaban")
        fig_area = px.area(df_filtered, x='timestamp', y=sensor_cols)
        st.plotly_chart(fig_area, use_container_width=True)
        st.write("Keterangan: Menggambarkan fluktuasi kadar air tanah secara kumulatif berdasarkan waktu.")

    with col4:
        st.subheader("Visualisasi 4: Rata-rata Nilai Sensor")
        avg_values = df_filtered[sensor_cols].mean().reset_index()
        avg_values.columns = ['Sensor', 'Rata-rata']
        fig_bar = px.bar(avg_values, x='Sensor', y='Rata-rata', color='Rata-rata', color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, use_container_width=True)
        st.write("Keterangan: Membandingkan tingkat kelembaban rata-rata antar titik sensor.")

    st.markdown("---")

    #Data Tabel
    st.subheader("Rekaman Data Historis")
    st.write("Keterangan Kolom Irrigasi: Kotak tercentang (v) adalah bukti sistem aktif, kotak kosong adalah bukti sistem mati.")
    st.dataframe(df_filtered, use_container_width=True)
    st.write("Selama periode 6-9 Maret 2020, sistem mencatat tidak ada aktivitas irigasi. Hal ini sesuai dengan tingkat kelembaban tanah rata-rata yang masih berada di atas ambang batas kritis.")
else:
    st.error("File data tidak ditemukan.")