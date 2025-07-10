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

st.header("📦 Manajemen Persediaan (EOQ)")
st.subheader("Studi Kasus: Kedai Kopi 'Kopi Kita'")

col1, col2 = st.columns([1.5, 2])

with col1:
    st.markdown("""
    **Skenario Bisnis:**
    'Kopi Kita' perlu menentukan jumlah pesanan biji kopi impor yang optimal untuk meminimalkan total biaya persediaan (biaya pesan dan biaya simpan).
    """)
    
    with st.container(border=True):
        st.subheader("⚙️ Parameter Model")
        # Nilai default disesuaikan kembali ke versi 'Kopi Kita'
        D = st.number_input("Permintaan Tahunan (kg)", min_value=1, value=1200)
        S = st.number_input("Biaya Pemesanan per Pesanan (Rp)", min_value=0, value=500000)
        H = st.number_input("Biaya Penyimpanan per kg per Tahun (Rp)", min_value=0, value=25000)
        lead_time = st.number_input("Lead Time Pengiriman (hari)", min_value=1, value=14)
        safety_stock = st.number_input("Stok Pengaman (Safety Stock) (kg)", min_value=0, value=10, help="Stok tambahan untuk mengantisipasi ketidakpastian permintaan atau keterlambatan.")
    
    with st.expander("Penjelasan Rumus Model: Economic Order Quantity (EOQ)"):
        st.markdown("""
        **Variabel Utama:**
        - **D (Permintaan Tahunan):** Total jumlah unit yang dibutuhkan selama satu tahun.
        - **S (Biaya Pemesanan):** Biaya tetap yang dikeluarkan setiap kali melakukan pemesanan.
        - **H (Biaya Penyimpanan):** Biaya untuk menyimpan satu unit barang selama satu tahun.
        - **Q (Kuantitas Pesanan):** Jumlah unit yang dipesan setiap kali melakukan pemesanan.
        - **TC (Total Biaya):** Penjumlahan dari total biaya pemesanan tahunan dan total biaya penyimpanan tahunan.
        - **ROP (Reorder Point):** Titik stok di mana pemesanan baru harus dilakukan.
        """)

        # Rumus utama EOQ
        st.markdown("**Rumus Utama:**")
        st.latex(r''' Q^* = \sqrt{\frac{2DS}{H}} ''')

        # Rumus Pendukung ROP dan TC
        st.markdown("**Rumus Pendukung:**")
        st.latex(r'''ROP = (\text{Permintaan Harian}) \times \text{Lead Time} + \text{Stok Pengaman}''')
        st.latex(r''' TC = \left(\frac{D}{Q}\right)S + \left(\frac{Q}{2}\right)H ''')

    # Perhitungan utama berdasarkan input
    if H > 0 and D > 0:
        eoq = math.sqrt((2 * D * S) / H)
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
        frekuensi_pesanan = 0 # Ensure frekuensi_pesanan is defined even if H or D is 0

    # Proses Perhitungan EOQ, ROP, dan TC    
    with st.expander("Lihat Proses Perhitungan"):
        st.markdown(f"**1. Perhitungan EOQ ($Q^*$):**")
        if H > 0 and D > 0:
            st.latex(fr"Q^* = \sqrt{{\frac{{2 \times {D} \times {S}}}{{{H}}}}} = {eoq:.2f} \text{{ unit}}")
        else:
            st.markdown("Tidak dapat menghitung EOQ karena biaya penyimpanan atau permintaan tahunan adalah nol.")
        
        st.markdown(f"**2. Perhitungan Titik Pemesanan Ulang (ROP):**")
        st.latex(fr"ROP = ({D}/360 \times {lead_time}) + {safety_stock} = {rop:.2f} \text{{ unit}}")
        
        st.markdown(f"**3. Perhitungan Biaya Total Tahunan:**")
        if np.isfinite(eoq) and eoq > 0:
            st.latex(fr"TC = \left(\frac{{{D}}}{{{eoq:.2f}}}\right){S} + \left(\frac{{{eoq:.2f}}}{{2}}\right){H} = \text{{Rp }}{total_biaya:,.2f}")
        else:
            st.markdown("Tidak dapat menghitung Total Biaya karena EOQ tidak valid.")

with col2:
    st.subheader("💡 Hasil dan Wawasan Bisnis")
    st.success(f"**Kebijakan Optimal:** Pesan **{eoq:.0f} kg** biji kopi setiap kali stok mencapai **{rop:.1f} kg**.")
    
    col1_res, col2_res = st.columns(2)
    with col1_res:
        st.metric(label="📦 Kuantitas Pesanan Optimal (EOQ)", value=f"{eoq:.0f} kg")
        st.metric(label="🎯 Titik Pemesanan Ulang (ROP)", value=f"{rop:.1f} kg")
    with col2_res:
        st.metric(label="💰 Total Biaya Persediaan Tahunan", value=f"Rp {total_biaya:,.0f}")
        st.metric(label="🔄 Siklus Pemesanan", value=f"~{siklus_pemesanan:.1f} hari")

    with st.container(border=True):
        st.markdown("**Analisis Kebijakan Persediaan:**")
        if eoq > 0:
            if eoq > (D/4):
                st.warning("- **Frekuensi Rendah:** Pesanan dalam jumlah besar tapi jarang. Ini hemat biaya pesan, tapi boros biaya simpan.")
            elif eoq < (D/12):
                st.info("- **Frekuensi Tinggi:** Pesanan dalam jumlah kecil tapi sering. Ini hemat biaya simpan, tapi boros biaya administrasi pemesanan.")
            else:
                st.success("- **Kebijakan Seimbang:** Kuantitas pesanan Anda menyeimbangkan biaya pesan dan biaya simpan dengan baik.")
        else:
            st.info("- Tidak ada analisis kebijakan yang tersedia karena EOQ tidak valid.")
    
    # Ini code untuk membuat grafik visualisasi analisis biaya
    st.markdown("#### Visualisasi Analisis Biaya")
    if eoq > 0:
        q_min_plot = max(1, eoq * 0.1)
        q_max_plot = eoq * 2.5 
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
        if eoq > 0:
            ax.axvline(x=eoq, color='purple', linestyle='--', label=f'EOQ')
            ax.annotate(f'Biaya Terendah\nRp {total_biaya:,.0f}', xy=(eoq, total_biaya), 
                        xytext=(eoq + (q_max_plot - q_min_plot) * 0.1, total_biaya * 0.6), 
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

    # Ini code untuk membuat grafik visualisasi siklus persediaan
    st.markdown("#### Visualisasi Siklus Persediaan")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    if siklus_pemesanan > 0 and eoq > 0:
        t_total = siklus_pemesanan * 2 
        t = np.linspace(0, t_total, 200)
        stok_level = []
        for time_point in t:
            sisa_waktu_siklus = time_point % siklus_pemesanan
            stok = (eoq + safety_stock) - permintaan_harian * sisa_waktu_siklus
            stok_level.append(max(stok, safety_stock)) 
            
        ax2.plot(t, stok_level, label='Tingkat Persediaan')
        ax2.axhline(y=rop, color='orange', linestyle='--', label=f'ROP ({rop:.1f} kg)')
        ax2.axhline(y=safety_stock, color='red', linestyle=':', label=f'Stok Pengaman ({safety_stock} kg)')
        
        if permintaan_harian > 0:
            time_to_reach_rop = (eoq / permintaan_harian) 
            for i in range(int(t_total / siklus_pemesanan) + 1):
                order_time = (i * siklus_pemesanan) + time_to_reach_rop
                if order_time <= t_total:
                    ax2.scatter(order_time, rop, color='red', s=100, zorder=5)
                    ax2.annotate('Pesan Ulang!', xy=(order_time, rop), 
                                 xytext=(order_time, rop + eoq*0.3),
                                 arrowprops=dict(facecolor='red', shrink=0.05))

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
        - **Garis Biru:** Menunjukkan tingkat persediaan yang terus menurun seiring penjualan harian.
        - **Garis Oranye (ROP):** Ketika stok menyentuh garis ini, inilah saatnya untuk memesan barang baru.
        - **Garis Merah (Stok Pengaman):** Stok minimum yang harus dijaga untuk menghindari kehabisan barang jika terjadi keterlambatan pengiriman.
        - **Siklus:** Stok akan kembali penuh (ke level EOQ + Stok Pengaman) setelah pesanan baru tiba.
        """)

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit.")
