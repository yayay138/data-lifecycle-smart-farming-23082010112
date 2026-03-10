import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Dashboard",
    
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #f0f4f0; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #1b5e20; }
    h2, h3 { color: #2e7d32; }
</style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("outputs/cleaned_data.csv")
    df["timestamp"]    = pd.to_datetime(df["timestamp"])
    df["date"]         = df["timestamp"].dt.date
    df["hour"]         = df["timestamp"].dt.hour
    moisture_cols      = ["moisture0","moisture1","moisture2","moisture3","moisture4"]
    df["avg_moisture"] = df[moisture_cols].mean(axis=1)
    return df

df = load_data()
moisture_cols = ["moisture0","moisture1","moisture2","moisture3","moisture4"]
sensor_labels = {
    "moisture0": "Sensor 0",
    "moisture1": "Sensor 1",
    "moisture2": "Sensor 2",
    "moisture3": "Sensor 3",
    "moisture4": "Sensor 4",
}
COLORS = ["#1565c0","#c62828","#e65100","#4a148c","#00695c"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filter Data")

    ts_min        = df["timestamp"].min()
    ts_max        = df["timestamp"].max()
    total_minutes = int((ts_max - ts_min).total_seconds() / 60)

    st.markdown("** Rentang Waktu**")
    slider_range = st.slider(
        label="Geser untuk filter waktu",
        min_value=0,
        max_value=total_minutes,
        value=(0, total_minutes),
        step=1,
        format="%d mnt",
        label_visibility="collapsed",
    )
    start_ts = ts_min + timedelta(minutes=int(slider_range[0]))
    end_ts   = ts_min + timedelta(minutes=int(slider_range[1]))
    st.caption(f" **Dari:** {start_ts.strftime('%d %b %Y %H:%M')}")
    st.caption(f" **Sampai:** {end_ts.strftime('%d %b %Y %H:%M')}")

    st.markdown("---")

    selected_sensors = st.multiselect(
        "Pilih Sensor",
        options=moisture_cols,
        default=moisture_cols,
        format_func=lambda x: sensor_labels[x],
    )

    resample_freq = st.selectbox(
        " Resolusi Waktu",
        options=["1min","5min","15min","30min","1h","3h","6h","12h","1D"],
        index=4,
        format_func=lambda x: {
            "1min":"1 Menit","5min":"5 Menit","15min":"15 Menit",
            "30min":"30 Menit","1h":"1 Jam","3h":"3 Jam",
            "6h":"6 Jam","12h":"12 Jam","1D":"1 Hari",
        }[x],
    )

 
    

#  Filter
filtered = df[(df["timestamp"] >= start_ts) & (df["timestamp"] <= end_ts)].copy()
if not selected_sensors:
    selected_sensors = moisture_cols

# Header 
st.title("Dashboard")
st.markdown("**Pemantauan kelembaban tanah dari 5 sensor IoT** — 6 hingga 9 Maret 2020")
st.markdown("---")

kpi_cols = st.columns(5)
for col_name, ui_col in zip(moisture_cols, kpi_cols):
    avg_val = filtered[col_name].mean()
    min_val = filtered[col_name].min()
    max_val = filtered[col_name].max()
    with ui_col:
        st.metric(
            label=f" {sensor_labels[col_name]}",
            value=f"{avg_val:.3f}",
            delta=f"↕ {min_val:.2f} – {max_val:.2f}",
        )
st.markdown("---")

def base_layout(fig, title=""):
    dark = "#212121"
    fig.update_layout(
        title=dict(text=title, font=dict(color="#1b5e20", size=15)),
        plot_bgcolor="#f9fbe7",
        paper_bgcolor="white",
        font=dict(color=dark, size=12),
        margin=dict(l=50, r=30, t=60, b=50),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#c5e1a5", borderwidth=1,
            font=dict(color=dark),
        ),
    )
    fig.update_xaxes(gridcolor="#e8f5e9", linecolor="#9e9e9e",
                     tickfont=dict(color=dark), title_font=dict(color=dark))
    fig.update_yaxes(gridcolor="#e8f5e9", linecolor="#9e9e9e",
                     tickfont=dict(color=dark), title_font=dict(color=dark))
    return fig

#Line chart 
st.subheader("Tren Kelembaban Tanah dari Waktu ke Waktu")

ts_df = (
    filtered.set_index("timestamp")[selected_sensors]
    .resample(resample_freq).mean().reset_index()
)
ts_long = ts_df.melt(id_vars="timestamp", var_name="sensor", value_name="moisture")
ts_long["sensor"] = ts_long["sensor"].map(sensor_labels)

fig1 = px.line(ts_long, x="timestamp", y="moisture", color="sensor",
               labels={"timestamp":"Waktu","moisture":"Kelembaban","sensor":"Sensor"},
               color_discrete_sequence=COLORS)
fig1 = base_layout(fig1, "Kelembaban Tanah per Sensor")
fig1.update_layout(hovermode="x unified",
                   legend=dict(orientation="h", yanchor="bottom", y=1.02,
                               xanchor="right", x=1))
fig1.update_yaxes(range=[0, 1])
st.plotly_chart(fig1, use_container_width=True)

#Box plot
st.subheader("Distribusi Kelembaban per Sensor")

box_long = filtered[selected_sensors].melt(var_name="sensor", value_name="moisture")
box_long["sensor"] = box_long["sensor"].map(sensor_labels)

fig2 = px.box(box_long, x="sensor", y="moisture", color="sensor",
              labels={"sensor":"Sensor","moisture":"Kelembaban"},
              color_discrete_sequence=COLORS, points="outliers")
fig2 = base_layout(fig2, "Distribusi Nilai Kelembaban tiap Sensor")
fig2.update_layout(showlegend=False)
fig2.update_yaxes(range=[0, 1])
st.plotly_chart(fig2, use_container_width=True)

#Heatmap Jam × Hari 
st.subheader(" 3 — Heatmap Kelembaban Rata-rata (Jam × Hari)")

heat_df = (
    filtered.groupby(["date","hour"])["avg_moisture"]
    .mean().reset_index()
    .pivot(index="date", columns="hour", values="avg_moisture")
)
fig3 = px.imshow(heat_df,
                 labels=dict(x="Jam dalam Sehari", y="Tanggal", color="Kelembaban"),
                 color_continuous_scale="YlGn", aspect="auto",
                 zmin=0, zmax=1, text_auto=".2f")
dark = "#212121"
fig3.update_layout(
    title=dict(text="Rata-rata Kelembaban (semua sensor) — Per Jam per Hari",
               font=dict(color="#1b5e20", size=15)),
    paper_bgcolor="white",
    font=dict(color=dark, size=11),
    margin=dict(l=50, r=30, t=60, b=50),
    coloraxis_colorbar=dict(
        title=dict(text="Kelembaban", font=dict(color=dark)),
        tickfont=dict(color=dark),
    ),
)
fig3.update_xaxes(tickfont=dict(color=dark), title_font=dict(color=dark))
fig3.update_yaxes(tickfont=dict(color=dark), title_font=dict(color=dark))
fig3.update_traces(textfont=dict(color=dark))
st.plotly_chart(fig3, use_container_width=True)


#Histogram
st.subheader("4 — Histogram Distribusi Kelembaban")

hist_long = filtered[selected_sensors].melt(var_name="sensor", value_name="moisture")
hist_long["sensor"] = hist_long["sensor"].map(sensor_labels)

fig5 = px.histogram(hist_long, x="moisture", color="sensor",
                    nbins=40, barmode="overlay", opacity=0.75,
                    labels={"moisture":"Nilai Kelembaban","count":"Frekuensi","sensor":"Sensor"},
                    color_discrete_sequence=COLORS)
fig5 = base_layout(fig5, "Distribusi Frekuensi Kelembaban per Sensor")
fig5.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02,
                               xanchor="right", x=1))
fig5.update_xaxes(range=[0, 1])
st.plotly_chart(fig5, use_container_width=True)

