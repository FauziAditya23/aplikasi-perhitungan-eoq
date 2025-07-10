import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd # Untuk tampilan tabel
from scipy.stats import norm # Untuk perhitungan Z-score yang lebih akurat
import math # Import modul math untuk fungsi sqrt

def format_rupiah(value):
    """
    Memformat nilai numerik ke dalam format Rupiah dengan pemisah ribuan.
    Menghilangkan .00 jika nilai adalah bilangan bulat.
    """
    if not np.isfinite(value):
        return "Tak Terhingga"
    if value == int(value):
        return f"Rp {int(value):,}"
    return f"Rp {value:,.2f}"

def calculate_eoq(D, S, H):
    """
    Menghitung Economic Order Quantity (EOQ).
    D: Permintaan tahunan (unit)
    S: Biaya pemesanan per pesanan
    H: Biaya penyimpanan per unit per tahun
    """
    if H == 0:
        return float('inf') # Menghindari pembagian dengan nol
    eoq = np.sqrt((2 * D * S) / H)
    return eoq

def calculate_total_inventory_cost(D, S, H, Q):
    """
    Menghitung total biaya persediaan.
    D: Permintaan tahunan (unit)
    S: Biaya pemesanan per pesanan
    H: Biaya penyimpanan per unit per tahun
    Q: Kuantitas pesanan (EOQ atau kuantitas lain)
    """
    if Q <= 0 or not np.isfinite(Q): # Mengubah kondisi untuk Q agar tidak nol, negatif, atau tak terhingga
        return float('inf'), float('inf'), float('inf')
    ordering_cost = (D / Q) * S
    holding_cost = (Q / 2) * H
    total_cost = ordering_cost + holding_cost
    return ordering_cost, holding_cost, total_cost # Mengembalikan ketiga nilai

def calculate_orders_per_year(D, Q):
    """
    Menghitung jumlah pemesanan per tahun.
    D: Permintaan tahunan (unit)
    Q: Kuantitas pesanan (EOQ atau kuantitas lain)
    """
    if Q <= 0 or not np.isfinite(Q): # Mengubah kondisi untuk Q agar tidak nol, negatif, atau tak terhingga
        return float('inf')
    orders = D / Q
    return orders

# Fungsi calculate_safety_stock dan calculate_reorder_point tidak digunakan
# karena safety_stock adalah input langsung dalam antarmuka ini.

st.set_page_config(layout="wide", page_title="EOQ & Inventory Model Simulator", page_icon="📈")

st.title("📦 Optimalisasi Manajemen Persediaan (EOQ & ROP)")
st.subheader("Studi Kasus: Kedai Kopi 'Kopi Kita'")

st.markdown("""
Selamat datang di alat simulasi interaktif untuk **Economic Order Quantity (EOQ)** dan **Reorder Point (ROP)**!
Aplikasi ini dirancang untuk membantu Anda menemukan strategi pemesanan optimal yang meminimalkan total biaya persediaan
sambil memastikan ketersediaan stok yang memadai. Mari kita optimalkan rantai pasok Anda! 🚀
""")

st.divider() # Garis pemisah visual

col1, col2 = st.columns([1.5, 2])

with col1:
    st.markdown("""
    **Skenario Bisnis:**
    'Kopi Kita' adalah kedai kopi yang sedang berkembang dan menghadapi tantangan dalam mengelola persediaan biji kopi impor.
    Tujuan utama adalah menentukan jumlah pesanan biji kopi yang paling efisien untuk meminimalkan total biaya persediaan,
    yang mencakup biaya pemesanan dan biaya penyimpanan.
    """)
    
    with st.container(border=True):
        st.header("⚙️ Parameter Model Input")
        # Nilai default disesuaikan kembali ke versi 'Kopi Kita'
        D = st.number_input("Permintaan Tahunan (kg) 📈", min_value=1, value=1200, help="Jumlah total unit biji kopi yang dibutuhkan dalam setahun.")
        S = st.number_input("Biaya Pemesanan per Pesanan (Rp) 💸", min_value=0, value=500000, help="Biaya tetap untuk setiap kali melakukan pemesanan (misalnya biaya administrasi, pengiriman).")
        H = st.number_input("Biaya Penyimpanan per kg per Tahun (Rp) 🏦", min_value=0, value=25000, help="Biaya untuk menyimpan satu kg biji kopi selama setahun (misalnya biaya gudang, asuransi, kerusakan).")
        
        st.markdown("---") # Pemisah dalam container
        st.subheader("🛡️ Parameter Stok Pengaman & ROP")
        lead_time = st.number_input("Lead Time Pengiriman (hari) ⏳", min_value=1, value=14, help="Jumlah hari antara pemesanan dan penerimaan biji kopi.")
        safety_stock = st.number_input("Stok Pengaman (Safety Stock) (kg) 🚨", min_value=0, value=10, help="Stok tambahan yang dijaga untuk mengantisipasi ketidakpastian permintaan atau keterlambatan pengiriman.")
    
    with st.expander("📚 Penjelasan Rumus Model: Economic Order Quantity (EOQ)"):
        st.markdown("""
        Model EOQ adalah metode manajemen persediaan yang menghitung kuantitas pesanan optimal untuk meminimalkan total biaya persediaan.
        """)
        st.markdown("**Variabel Utama:**")
        st.markdown("""
        - **D (Permintaan Tahunan):** Total jumlah unit yang dibutuhkan selama satu tahun.
        - **S (Biaya Pemesanan):** Biaya tetap yang dikeluarkan setiap kali melakukan pemesanan.
        - **H (Biaya Penyimpanan):** Biaya untuk menyimpan satu unit barang selama satu tahun.
        - **Q (Kuantitas Pesanan):** Jumlah unit yang dipesan setiap kali melakukan pemesanan.
        - **TC (Total Biaya):** Penjumlahan dari total biaya pemesanan tahunan dan total biaya penyimpanan tahunan.
        - **ROP (Reorder Point):** Titik stok di mana pemesanan baru harus dilakukan.
        """)

        st.markdown("**Rumus Utama (EOQ):**")
        st.latex(r''' Q^* = \sqrt{\frac{2DS}{H}} ''')

        st.markdown("**Rumus Pendukung (ROP & TC):**")
        st.latex(r'''ROP = (\text{Permintaan Harian}) \times \text{Lead Time} + \text{Stok Pengaman}''')
        st.latex(r''' TC = \left(\frac{D}{Q}\right)S + \left(\frac{Q}{2}\right)H ''')

# Perhitungan utama berdasarkan input
# Perhitungan ini akan dijalankan setiap kali input berubah, tetapi hasilnya hanya ditampilkan
# setelah tombol "Hitung" ditekan.
if H > 0 and D > 0:
    eoq = calculate_eoq(D, S, H)
    frekuensi_pesanan = D / eoq if eoq > 0 else 0
    biaya_pemesanan = (D/eoq) * S if eoq > 0 else 0
    biaya_penyimpanan = (eoq/2) * H
    total_biaya = biaya_pemesanan + biaya_penyimpanan
    permintaan_harian = D / 360 # Menggunakan 360 hari untuk perhitungan harian
    rop = (permintaan_harian * lead_time) + safety_stock
    siklus_pemesanan = 360 / frekuensi_pesanan if frekuensi_pesanan > 0 else 0
else:
    eoq = 0
    total_biaya = 0
    rop = 0
    siklus_pemesanan = 0
    frekuensi_pesanan = 0

# Tombol untuk memicu perhitungan dan tampilan hasil
if st.button("✨ Hitung Optimalisasi Persediaan", type="primary"):
    with col2:
        st.header("💡 Hasil dan Wawasan Bisnis")
        st.success(f"**Kebijakan Optimal untuk 'Kopi Kita':** Pesan **{eoq:.0f} kg** biji kopi setiap kali stok mencapai **{rop:.1f} kg**.")
        
        col1_res, col2_res = st.columns(2)
        with col1_res:
            st.metric(label="📦 Kuantitas Pesanan Optimal (EOQ)", value=f"{eoq:.0f} kg")
            st.metric(label="🎯 Titik Pemesanan Ulang (ROP)", value=f"{rop:.1f} kg")
        with col2_res:
            st.metric(label="💰 Total Biaya Persediaan Tahunan", value=f"Rp {total_biaya:,.0f}")
            st.metric(label="🔄 Siklus Pemesanan", value=f"~{siklus_pemesanan:.1f} hari")

        st.divider() # Garis pemisah visual

        with st.container(border=True):
            st.subheader("📊 Analisis Kebijakan Persediaan")
            if eoq > 0:
                if eoq > (D/4):
                    st.warning("- **Frekuensi Rendah:** Pesanan dalam jumlah besar tapi jarang. Ini hemat biaya pesan, tapi boros biaya simpan.")
                elif eoq < (D/12):
                    st.info("- **Frekuensi Tinggi:** Pesanan dalam jumlah kecil tapi sering. Ini hemat biaya simpan, tapi boros biaya administrasi pemesanan.")
                else:
                    st.success("- **Kebijakan Seimbang:** Kuantitas pesanan Anda menyeimbangkan biaya pesan dan biaya simpan dengan baik.")
            else:
                st.info("- Tidak ada analisis kebijakan yang tersedia karena EOQ tidak valid (biaya penyimpanan atau permintaan tahunan nol).")
        
        st.divider() # Garis pemisah visual

        # Ini code untuk membuat grafik visualisasi analisis biaya
        st.subheader("📈 Visualisasi Analisis Biaya")
        if eoq > 0:
            q_min_plot = max(1, eoq * 0.1)
            q_max_plot = eoq * 2.5 # Memperluas rentang sedikit untuk melihat kurva lebih jelas
            q = np.linspace(q_min_plot, q_max_plot, 100)
        else:
            q = np.linspace(1, 200, 100) 

        q = q[q > 0]
        if not np.any(q): 
            st.warning("Tidak dapat membuat plot biaya karena rentang kuantitas pesanan tidak valid.")
        else:
            holding_costs = (q / 2) * H
            ordering_costs = (D / q) * S
            total_costs = holding_costs + ordering_costs
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(q, holding_costs, 'b-', label='Biaya Penyimpanan')
            ax.plot(q, ordering_costs, 'g-', label='Biaya Pemesanan')
            ax.plot(q, total_costs, 'r-', linewidth=3, label='Total Biaya')
            if eoq > 0 and np.isfinite(total_biaya):
                ax.axvline(x=eoq, color='purple', linestyle='--', label=f'EOQ: {eoq:,.2f} kg')
                ax.annotate(f'Biaya Terendah\nRp {total_biaya:,.0f}', xy=(eoq, total_biaya), 
                            xytext=(eoq * 1.1, total_biaya * 1.1), # Menyesuaikan posisi teks relatif
                            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8, headlength=8),
                            horizontalalignment='left', verticalalignment='bottom',
                            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.9))

            ax.set_xlabel('Kuantitas Pemesanan (kg)')
            ax.set_ylabel('Biaya Tahunan (Rp)')
            ax.set_title('Analisis Biaya Persediaan (EOQ)', fontsize=16)
            ax.legend()
            ax.grid(True)
            ax.ticklabel_format(style='plain', axis='y')
            ax.set_ylim(bottom=0)
            ax.set_xlim(left=q_min_plot)
            st.pyplot(fig)

            with st.container(border=True):
                st.markdown("**🔍 Penjelasan Grafik Analisis Biaya:**")
                st.markdown("""
                Grafik ini menunjukkan trade-off antara biaya pemesanan dan biaya penyimpanan.
                - **Garis Biru (Biaya Penyimpanan):** Semakin banyak barang yang dipesan, semakin tinggi biaya untuk menyimpannya.
                - **Garis Hijau (Biaya Pemesanan):** Semakin banyak barang yang dipesan dalam satu waktu, semakin jarang kita memesan, sehingga total biaya pemesanan tahunan menurun.
                - **Garis Merah (Total Biaya):** Adalah penjumlahan dari kedua biaya di atas.
                - **Garis Ungu (EOQ):** Menandai titik di mana kurva total biaya mencapai titik terendahnya. Ini adalah kuantitas pesanan yang paling efisien.
                """)

        st.divider() # Garis pemisah visual

        # Ini code untuk membuat grafik visualisasi siklus persediaan
        st.subheader("🔄 Visualisasi Siklus Persediaan")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        if siklus_pemesanan > 0 and eoq > 0:
            t_total = siklus_pemesanan * 2.5 # Menampilkan lebih dari dua siklus penuh untuk visualisasi yang lebih baik
            t = np.linspace(0, t_total, 200)
            stok_level = []
            for time_point in t:
                sisa_waktu_siklus = time_point % siklus_pemesanan
                stok = (eoq + safety_stock) - permintaan_harian * sisa_waktu_siklus
                stok_level.append(max(stok, safety_stock)) 
                
            ax2.plot(t, stok_level, label='Tingkat Persediaan')
            ax2.axhline(y=rop, color='orange', linestyle='--', label=f'ROP ({rop:.1f} kg)')
            ax2.axhline(y=safety_stock, color='red', linestyle=':') # Fixed syntax error here
            
            if permintaan_harian > 0:
                # Menambahkan titik pemesanan ulang pada grafik
                # Hitung waktu saat ROP tercapai dalam setiap siklus
                time_to_reach_rop_from_peak = (eoq / permintaan_harian) 
                
                # Menentukan titik-titik di mana pesanan baru tiba (stok naik)
                for i in range(int(t_total / siklus_pemesanan) + 1):
                    arrival_time = i * siklus_pemesanan
                    if arrival_time <= t_total:
                        # Tandai titik kedatangan stok baru
                        ax2.scatter(arrival_time, eoq + safety_stock, color='blue', marker='o', s=100, zorder=5, label='Stok Tiba' if i == 0 else "")
                        
                    # Tandai titik pemesanan ulang (saat stok mencapai ROP)
                    order_time = arrival_time - lead_time
                    if order_time >= 0 and order_time <= t_total:
                        ax2.scatter(order_time, rop, color='red', marker='X', s=100, zorder=5, label='Pesan Ulang' if i == 0 else "")
                        ax2.annotate('Pesan Ulang!', xy=(order_time, rop), 
                                     xytext=(order_time + t_total*0.05, rop + eoq*0.1), # Menyesuaikan posisi teks
                                     arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=8, headlength=8),
                                     horizontalalignment='left', verticalalignment='bottom',
                                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=0.5, alpha=0.9))


        ax2.set_xlabel('Waktu (Hari)')
        ax2.set_ylabel('Jumlah Stok (kg)')
        ax2.set_title('Simulasi Siklus Persediaan', fontsize=16)
        ax2.legend()
        ax2.grid(True)
        ax2.set_ylim(bottom=0)
        st.pyplot(fig2)

        with st.container(border=True):
            st.markdown("**🔍 Penjelasan Grafik Siklus:**")
            st.markdown("""
            Grafik ini menyimulasikan pergerakan stok dari waktu ke waktu.
            - **Garis Biru (Tingkat Persediaan):** Menunjukkan tingkat persediaan yang terus menurun seiring penjualan harian.
            - **Garis Oranye (ROP):** Ketika stok menyentuh garis ini, inilah saatnya untuk memesan barang baru.
            - **Garis Merah (Stok Pengaman):** Stok minimum yang harus dijaga untuk menghindari kehabisan barang jika terjadi keterlambatan pengiriman.
            - **Simbol 'X' Merah:** Menandakan titik di mana pesanan baru harus dilakukan (saat stok mencapai ROP).
            - **Simbol 'O' Biru:** Menandakan titik di mana pesanan baru tiba, dan tingkat stok kembali ke EOQ + Stok Pengaman.
            - **Siklus:** Stok akan kembali penuh (ke level EOQ + Stok Pengaman) setelah pesanan baru tiba.
            """)

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit.")
