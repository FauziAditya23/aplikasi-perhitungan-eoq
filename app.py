import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd # Untuk tampilan tabel
from scipy.stats import norm # Untuk perhitungan Z-score yang lebih akurat
import math # Import math for floor function

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
    S: Biaya pemesanan per pes pesanan
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

def calculate_safety_stock(z_score, std_dev_daily_demand, lead_time_days):
    """
    Menghitung Safety Stock (Persediaan Pengaman).
    z_score: Nilai Z yang sesuai dengan tingkat layanan
    std_dev_daily_demand: Standar deviasi permintaan harian
    lead_time_days: Waktu tunggu dalam hari
    """
    if lead_time_days <= 0 or std_dev_daily_demand < 0:
        return 0.0 # Mengembalikan float 0.0 untuk konsistensi
    safety_stock = z_score * std_dev_daily_demand * np.sqrt(lead_time_days)
    return safety_stock

def calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock):
    """
    Menghitung Reorder Point (Titik Pemesanan Kembali).
    avg_daily_demand: Rata-rata permintaan harian
    lead_time_days: Waktu tunggu dalam hari
    safety_stock: Persediaan pengaman
    """
    if lead_time_days < 0 or avg_daily_demand < 0:
        return 0.0 # Mengembalikan float 0.0 untuk konsistensi
    reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
    return reorder_point

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Model Matematika Industri", layout="wide", initial_sidebar_state="expanded")
st.title("📈 Dashboard Model Matematika untuk Industri")
st.markdown("Sebuah aplikasi interaktif untuk memahami penerapan model matematika kunci dalam skenario bisnis di dunia nyata.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Panduan Aplikasi")
    st.markdown("""
    Aplikasi ini mendemonstrasikan model matematika kunci dalam skenario bisnis di dunia nyata.
    Tab yang tersedia menyediakan **analisis, visualisasi, dan wawasan bisnis** yang dapat ditindaklanjuti.
    """)
    st.info("**Tips:** Ubah parameter di model untuk melihat bagaimana hasilnya berubah secara real-time!")
    
    st.markdown("""
    ---
    **📦 Model Persediaan (EOQ):**
    Menentukan kuantitas pesanan optimal untuk meminimalkan total biaya persediaan.
    """)
    st.divider()
    st.caption("Matematika Terapan | Teknik Informatika - Universitas Pelita Bangsa")

# --- TAB 2: MODEL PERSEDIAAN ---
def model_persediaan():
    st.header("📦 Manajemen Persediaan (EOQ & ROP)")
    st.subheader("Studi Kasus: Kedai Kopi 'Kopi Kita'")

    col1, col2 = st.columns([1.5, 2])

    with col1:
        st.markdown("""
        **Skenario Bisnis:**
        'Kopi Kita' perlu menentukan jumlah pesanan biji kopi impor yang optimal untuk meminimalkan total biaya persediaan (biaya pesan dan biaya simpan),
        serta mengelola stok pengaman dan titik pemesanan kembali untuk menjaga kelancaran operasional.
        """)
        
        with st.container(border=True):
            st.subheader("⚙️ Parameter Model")
            D = st.number_input("Permintaan Tahunan (unit) 📈", min_value=1, value=10000, help="Jumlah total unit yang dibutuhkan dalam setahun.")
            S = st.number_input("Biaya Pemesanan (S) (Rp) 💸", min_value=1, value=60000, help="Biaya tetap untuk setiap kali melakukan pemesanan dalam Rupiah.")
            H = st.number_input("Biaya Penyimpanan (H) (Rp) 🏦", min_value=1, value=25000, help="Biaya untuk menyimpan satu unit barang selama setahun dalam Rupiah.")
            
            st.markdown("---")
            st.subheader("🛡️ Parameter Safety Stock & ROP")
            lead_time_days = st.number_input("Waktu Tunggu (Lead Time) (hari) ⏳", min_value=0, value=7, help="Jumlah hari antara pemesanan dan penerimaan barang.")
            service_level_percent = st.slider("Tingkat Layanan (Service Level) (%) 🎯", min_value=50, max_value=99, value=95, help="Probabilitas tidak terjadi kekurangan stok selama waktu tunggu.")
            std_dev_daily_demand = st.number_input("Standar Deviasi Permintaan Harian (unit) 📉", min_value=0.0, value=5.0, help="Variabilitas permintaan harian. Jika tidak tahu, coba estimasi.")

        with st.expander("Penjelasan Rumus Model: Economic Order Quantity (EOQ) & Reorder Point (ROP)"):
            st.markdown("""
            **Variabel Utama:**
            - **D (Permintaan Tahunan):** Total jumlah unit yang dibutuhkan selama satu tahun.
            - **S (Biaya Pemesanan):** Biaya tetap yang dikeluarkan setiap kali melakukan pemesanan.
            - **H (Biaya Penyimpanan):** Biaya untuk menyimpan satu unit barang selama satu tahun.
            - **Q (Kuantitas Pesanan):** Jumlah unit yang dipesan setiap kali melakukan pemesanan.
            - **TC (Total Biaya):** Penjumlahan dari total biaya pemesanan tahunan dan total biaya penyimpanan tahunan.
            - **ROP (Reorder Point):** Titik stok di mana pemesanan baru harus dilakukan.
            - **Safety Stock (Persediaan Pengaman):** Stok tambahan untuk melindungi dari variabilitas permintaan atau waktu tunggu.
            """)

            # Rumus utama EOQ
            st.markdown("**Rumus Utama EOQ:**")
            st.latex(r''' Q^* = \sqrt{\frac{2DS}{H}} ''')

            # Rumus Pendukung ROP dan TC
            st.markdown("**Rumus Pendukung:**")
            st.latex(r'''\text{Rata-rata Permintaan Harian} = \frac{\text{Permintaan Tahunan}}{365}''')
            st.latex(r'''\text{Z-score} = \text{Nilai dari distribusi normal standar (berdasarkan Tingkat Layanan)}''')
            st.latex(r'''\text{Safety Stock} = Z\text{-score} \times \text{Std Dev Permintaan Harian} \times \sqrt{\text{Waktu Tunggu (hari)}}''')
            st.latex(r'''ROP = (\text{Rata-rata Permintaan Harian} \times \text{Waktu Tunggu}) + \text{Safety Stock}''')
            st.latex(r''' TC = \left(\frac{D}{Q}\right)S + \left(\frac{Q}{2}\right)H ''')

    # Perhitungan (dipindahkan keluar dari tombol)
    if H > 0 and D > 0:
        eoq = calculate_eoq(D, S, H)
        
        ordering_cost_at_eoq, holding_cost_at_eoq, total_cost_at_eoq = calculate_total_inventory_cost(D, S, H, eoq)
        orders_per_year_at_eoq = calculate_orders_per_year(D, eoq)

        # Perhitungan ROP dan Safety Stock
        avg_daily_demand = D / 365.0
        z_score = norm.ppf(service_level_percent / 100.0)
        
        safety_stock = calculate_safety_stock(z_score, std_dev_daily_demand, lead_time_days)
        reorder_point = calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock)
        
        siklus_pemesanan = 365 / orders_per_year_at_eoq if orders_per_year_at_eoq > 0 else 0
    else:
        eoq = 0.0
        total_cost_at_eoq = 0.0
        orders_per_year_at_eoq = 0.0
        safety_stock = 0.0
        reorder_point = 0.0
        siklus_pemesanan = 0.0
        avg_daily_demand = 0.0
        z_score = 0.0

    with col2:
        st.subheader("💡 Hasil dan Wawasan Bisnis")

        # Menampilkan hasil dalam bentuk metrik yang lebih menarik
        col1_res, col2_res, col3_res = st.columns(3)
        with col1_res:
            st.metric("📦 Economic Order Quantity (EOQ)", f"{eoq:,.0f} unit") # Dibulatkan ke integer
            st.caption("Jumlah pesanan optimal yang meminimalkan total biaya.")
        with col2_res:
            st.metric("💰 Total Biaya Persediaan (pada EOQ)", format_rupiah(total_cost_at_eoq))
            st.caption("Total biaya yang dikeluarkan jika memesan sejumlah EOQ.")
        with col3_res:
            st.metric("🔄 Jumlah Pemesanan per Tahun (pada EOQ)", f"{orders_per_year_at_eoq:,.1f} kali")
            st.caption("Frekuensi pemesanan dalam setahun.")

        st.markdown("---") # Garis pemisah

        st.subheader("🛡️ Hasil Perhitungan Safety Stock & Reorder Point")
        col_ss, col_rop, col_siklus = st.columns(3)
        with col_ss:
            st.metric("🛡️ Safety Stock (Persediaan Pengaman)", f"{safety_stock:,.0f} unit") # Dibulatkan ke integer
            st.caption("Stok ekstra untuk melindungi dari variabilitas permintaan atau waktu tunggu.")
        with col_rop:
            st.metric("🔔 Reorder Point (Titik Pemesanan Kembali)", f"{reorder_point:,.0f} unit") # Dibulatkan ke integer
            st.caption("Tingkat persediaan di mana pesanan baru harus dilakukan.")
        with col_siklus:
            # Updated to include orders per year in the format "18.6 hari (20x pertahun)"
            if np.isfinite(siklus_pemesanan) and np.isfinite(orders_per_year_at_eoq):
                st.metric("🗓️ Siklus Pemesanan (EOQ)", f"~{siklus_pemesanan:,.1f} hari ({orders_per_year_at_eoq:,.0f}x pertahun)")
            else:
                st.metric("🗓️ Siklus Pemesanan (EOQ)", "Tak Terhingga")
            st.caption("Rata-rata durasi antar pesanan.")
        
        st.markdown("---") # Garis pemisah

        # Analisis Kebijakan Persediaan
        with st.container(border=True):
            st.markdown("**Analisis Kebijakan Persediaan:**")
            if eoq == float('inf'):
                st.info("- EOQ tak terhingga: Ini terjadi jika biaya penyimpanan sangat rendah atau nol. Pertimbangkan untuk memesan dalam jumlah sangat besar atau sesuai kapasitas gudang.")
            elif total_cost_at_eoq == float('inf'):
                st.info("- Total biaya tak terhingga: Periksa input Anda, terutama jika kuantitas pesanan mendekati nol atau permintaan/biaya tidak valid.")
            elif orders_per_year_at_eoq > 12:
                st.warning("- **Frekuensi Pemesanan Tinggi:** Memesan terlalu sering dapat meningkatkan biaya administrasi dan logistik, meskipun biaya penyimpanan rendah.")
            elif orders_per_year_at_eoq < 2:
                st.warning("- **Frekuensi Pemesanan Rendah:** Memesan terlalu jarang dapat menyebabkan biaya penyimpanan tinggi dan risiko kehabisan stok jika ada lonjakan permintaan.")
            else:
                st.success("- **Kebijakan Optimal:** Kuantitas pesanan Anda menyeimbangkan biaya pemesanan dan biaya penyimpanan dengan baik. Ikuti rekomendasi EOQ dan ROP untuk efisiensi maksimal.")
            
            if safety_stock > 0 and reorder_point > 0:
                st.info(f"- **Manajemen Risiko:** Dengan Safety Stock sebesar {safety_stock:,.0f} unit, Anda memiliki bantalan untuk {service_level_percent}% tingkat layanan, mengurangi risiko kehabisan stok.")
            elif safety_stock == 0:
                st.warning("- **Tanpa Safety Stock:** Anda berisiko tinggi kehabisan stok jika ada variabilitas permintaan atau keterlambatan pengiriman. Pertimbangkan untuk menambahkan Safety Stock.")


    st.markdown("---") # Garis pemisah

    st.subheader("📋 Ringkasan Hasil")
    summary_data = {
        "Metrik": ["Economic Order Quantity (EOQ)", "Total Biaya Persediaan (pada EOQ)", "Jumlah Pemesanan per Tahun (pada EOQ)", "Safety Stock (Persediaan Pengaman)", "Reorder Point (Titik Pemesanan Kembali)", "Siklus Pemesanan (EOQ)"],
        "Nilai": [
            f"{eoq:,.0f} unit" if np.isfinite(eoq) else "Tak Terhingga",
            format_rupiah(total_cost_at_eoq),
            f"{orders_per_year_at_eoq:,.1f} kali" if np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga",
            f"{safety_stock:,.0f} unit",
            f"{reorder_point:,.0f} unit",
            f"~{siklus_pemesanan:,.1f} hari ({orders_per_year_at_eoq:,.0f}x pertahun)" if np.isfinite(siklus_pemesanan) and np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga" # Updated here too
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    # Mengatur indeks agar dimulai dari 1
    df_summary.index = np.arange(1, len(df_summary) + 1)
    st.table(df_summary)

    st.markdown("---") # Garis pemisah

    # Menggunakan expander untuk detail perhitungan
    with st.expander("➕ Lihat Detail Perhitungan Matematika"):
        st.markdown("Berikut adalah langkah-langkah perhitungan berdasarkan input Anda:")

        st.markdown("#### 1. Perhitungan Economic Order Quantity (EOQ)")
        st.latex(r'''
            EOQ = \sqrt{\frac{2 \times D \times S}{H}}
        ''')
        st.markdown(f"""
        Di mana:
        * $D$ = Permintaan Tahunan = {D} unit
        * $S$ = Biaya Pemesanan = {format_rupiah(S)}
        * $H$ = Biaya Penyimpanan = {format_rupiah(H)}
        """)
        st.latex(fr'''
            EOQ = \sqrt{{\frac{{2 \times {D} \times {S}}}{{{H}}}}}
        ''')
        st.latex(fr'''
            EOQ = \sqrt{{\frac{{{2 * D * S}}}{{{H}}}}}
        ''')
        if H > 0:
            st.latex(fr'''
                EOQ = \sqrt{{{ (2 * D * S) / H:,.2f}}}
            ''')
            st.latex(fr'''
                EOQ = {eoq:,.2f} \text{{ unit}}
            ''')
        else:
            st.write("EOQ tak terhingga karena biaya penyimpanan adalah nol.")


        st.markdown("#### 2. Perhitungan Total Biaya Persediaan (pada EOQ)")
        st.latex(r'''
            \text{Total Biaya} = \text{Biaya Pemesanan} + \text{Biaya Penyimpanan}
        ''')
        st.latex(r'''
            \text{Biaya Pemesanan} = \left(\frac{D}{Q}\right) \times S
        ''')
        st.latex(r'''
            \text{Biaya Penyimpanan} = \left(\frac{Q}{2}\right) \times H
        ''')
        st.markdown(f"""
        Dengan $Q = EOQ = {eoq:,.2f}$ unit:
        """)
        if np.isfinite(eoq) and eoq > 0:
            st.latex(fr'''
                \text{{Biaya Pemesanan}} = \left(\frac{{{D}}}{{{eoq:,.2f}}}\right) \times {format_rupiah(S).replace('Rp ', '')}
            ''')
            st.latex(fr'''
                \text{{Biaya Pemesanan}} = {format_rupiah((D / eoq) * S)}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = \left(\frac{{{eoq:,.2f}}}{{2}}\right) \times {format_rupiah(H).replace('Rp ', '')}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = {format_rupiah((eoq / 2) * H)}
            ''')
            st.latex(fr'''
                \text{{Total Biaya}} = {format_rupiah(ordering_cost_at_eoq).replace('Rp ', '')} + {format_rupiah(holding_cost_at_eoq).replace('Rp ', '')}
            ''')
            st.latex(fr'''
                \text{{Total Biaya}} = {format_rupiah(total_cost_at_eoq)}
            ''')
        else:
            st.write("Perhitungan biaya tidak dapat ditampilkan karena EOQ tak terhingga atau tidak valid.")


        st.markdown("#### 3. Perhitungan Jumlah Pemesanan per Tahun (pada EOQ)")
        st.latex(r'''
            \text{Jumlah Pemesanan per Tahun} = \frac{D}{Q}
        ''')
        st.markdown(f"""
        Dengan $Q = EOQ = {eoq:,.2f}$ unit:
        """)
        if np.isfinite(eoq) and eoq > 0:
            st.latex(fr'''
                \text{{Jumlah Pemesanan per Tahun}} = \frac{{{D}}}{{{eoq:,.2f}}}
            ''')
            st.latex(fr'''
                \text{{Jumlah Pemesanan per Tahun}} = {orders_per_year_at_eoq:,.2f} \text{{ kali}}
            ''')
        else:
            st.write("Jumlah pemesanan per tahun tidak dapat ditampilkan karena EOQ tak terhingga atau tidak valid.")

        st.markdown("#### 4. Perhitungan Safety Stock (Persediaan Pengaman)")
        st.latex(r'''
            \text{Rata-rata Permintaan Harian} = \frac{\text{Permintaan Tahunan}}{365}
        ''')
        st.latex(fr'''
            \text{{Rata-rata Permintaan Harian}} = \frac{{{D}}}{{365}} = {avg_daily_demand:,.2f} \text{{ unit/hari}}
        ''')
        st.latex(r'''
            Z\text{-score} = \text{Nilai dari distribusi normal standar}
        ''')
        st.markdown(f"Untuk tingkat layanan {service_level_percent}%, Z-score adalah sekitar {z_score:,.2f}.")
        st.latex(fr'''\text{{Z-score}} = {z_score:,.2f}''')
        st.latex(r'''
            \text{Safety Stock} = Z\text{-score} \times \text{Std Dev Permintaan Harian} \times \sqrt{\text{Waktu Tunggu (hari)}}
        ''')
        st.markdown(f"""
        Di mana:
        * $Z\text{-score}$ = {z_score:,.2f}
        * $\text{{Std Dev Permintaan Harian}}$ = {std_dev_daily_demand:,.2f} unit
        * $\text{{Waktu Tunggu}}$ = {lead_time_days} hari
        """)
        st.latex(fr'''
            \text{{Safety Stock}} = {z_score:,.2f} \times {std_dev_daily_demand:,.2f} \times {np.sqrt(lead_time_days):,.2f}
            ''')
        st.latex(fr'''
            \text{{Safety Stock}} = {safety_stock:,.2f} \text{{ unit}}
        ''')

        st.markdown("#### 5. Perhitungan Reorder Point (Titik Pemesanan Kembali)")
        st.latex(r'''
            \text{Reorder Point} = (\text{Rata-rata Permintaan Harian} \times \text{Waktu Tunggu (hari)}) + \text{Safety Stock}
        ''')
        st.markdown(f"""
        Di mana:
        * $\text{{Rata-rata Permintaan Harian}}$ = {avg_daily_demand:,.2f} unit/hari
        * $\text{{Waktu Tunggu}}$ = {lead_time_days} hari
        * $\text{{Safety Stock}}$ = {safety_stock:,.2f} unit
        """)
        st.latex(fr'''
            \text{{Reorder Point}} = ({avg_daily_demand:,.2f} \times {lead_time_days}) + {safety_stock:,.2f}
        ''')
        st.latex(fr'''
            \text{{Reorder Point}} = { (avg_daily_demand * lead_time_days):,.2f} + {safety_stock:,.2f}
        ''')
        st.latex(fr'''
            \text{{Reorder Point}} = {reorder_point:,.2f} \text{{ unit}}
        ''')

    st.markdown("---") # Garis pemisah

    st.subheader("📈 Visualisasi Biaya Persediaan")

    # Buat rentang kuantitas pesanan untuk grafik
    # Pastikan rentang mencakup EOQ dan kuantitas kustom, dan selalu terhingga
    if np.isfinite(eoq) and eoq > 0:
        max_q_value = eoq * 2.5 # Membuat batas atas sumbu X sekitar 2.5 kali EOQ
    else:
        max_q_value = D * 0.5 # Fallback jika EOQ tak terhingga atau nol, gunakan sebagian dari permintaan tahunan

    # Memastikan nilai minimum yang masuk akal untuk max_q_value agar grafik tidak terlalu sempit
    max_q_value = max(max_q_value, 100) # Pastikan setidaknya ada rentang 100 unit

    q_values = np.linspace(1, max_q_value, 500)
    
    ordering_costs_plot = [(D / q) * S for q in q_values]
    holding_costs_plot = [(q / 2) * H for q in q_values]
    total_costs_plot = [oc + hc for oc, hc in zip(ordering_costs_plot, holding_costs_plot)]

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Mengatur urutan plot agar sesuai dengan legenda di gambar: Biaya Penyimpanan, Biaya Pemesanan, Total Biaya
    ax.plot(q_values, holding_costs_plot, label="Biaya Penyimpanan", color='blue') # Biru untuk Biaya Penyimpanan
    ax.plot(q_values, ordering_costs_plot, label="Biaya Pemesanan", color='green') # Hijau untuk Biaya Pemesanan
    ax.plot(q_values, total_costs_plot, label="Total Biaya", color='red', linewidth=2) # Merah untuk Total Biaya

    if np.isfinite(eoq) and eoq > 0:
        ax.axvline(eoq, color='purple', linestyle='--', label=f'EOQ') # Garis ungu putus-putus untuk EOQ
        # Menambahkan anotasi untuk titik biaya terendah
        if np.isfinite(total_cost_at_eoq):
            ax.annotate(f'Biaya Terendah\n{format_rupiah(total_cost_at_eoq)}',
                        xy=(eoq, total_cost_at_eoq),
                        # Menyesuaikan posisi teks dan properti panah untuk tampilan yang lebih baik
                        xytext=(eoq + max_q_value * 0.15, total_cost_at_eoq + total_cost_at_eoq * 0.1),
                        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8, headlength=8),
                        horizontalalignment='left', verticalalignment='bottom',
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.9))
    
    ax.set_xlabel("Kuantitas Pemesanan (unit)") # Mengubah label sumbu X
    ax.set_ylabel("Biaya Tahunan (Rp)") # Mengubah label sumbu Y
    ax.set_title("Analisis Biaya Persediaan (EOQ)", fontsize=16) # Mengubah judul grafik
    ax.legend()
    ax.grid(True, linestyle='-', alpha=0.7) # Mengubah gaya grid menjadi garis solid
    ax.set_ylim(bottom=0) # Memastikan sumbu y dimulai dari 0
    ax.ticklabel_format(style='plain', axis='y') # Menghilangkan notasi ilmiah pada sumbu Y
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
        # Simulasi beberapa siklus untuk visualisasi yang lebih baik
        num_cycles = 3 # Tampilkan 3 siklus penuh
        t_cycle = siklus_pemesanan
        t_total = t_cycle * num_cycles
        
        t = np.linspace(0, t_total, int(t_total * 10)) # Lebih banyak titik untuk kurva yang halus
        stok_level = []
        
        for time_point in t:
            current_cycle_time = time_point % t_cycle
            # Tingkat stok menurun dari (EOQ + safety_stock)
            stok = (eoq + safety_stock) - (avg_daily_demand * current_cycle_time)
            stok_level.append(max(stok, safety_stock)) # Stok tidak boleh di bawah safety stock

        ax2.plot(t, stok_level, label='Tingkat Persediaan', color='blue')
        ax2.axhline(y=reorder_point, color='orange', linestyle='--', label=f'ROP ({reorder_point:,.0f} unit)')
        ax2.axhline(y=safety_stock, color='red', linestyle=':', label=f'Stok Pengaman ({safety_stock:,.0f} unit)')
        
        # Menambahkan titik pemesanan ulang dan anotasi
        for i in range(num_cycles):
            order_time = (i * t_cycle) + (t_cycle - lead_time_days)
            if order_time >= 0: # Pastikan waktu pemesanan tidak negatif
                ax2.scatter(order_time, reorder_point, color='red', s=100, zorder=5, edgecolors='black')
                ax2.annotate('Pesan Ulang!', xy=(order_time, reorder_point), xytext=(order_time + t_cycle*0.05, reorder_point + eoq*0.1),
                             arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=8, headlength=8),
                             horizontalalignment='left', verticalalignment='bottom', fontsize=10, color='red')
        
        # Menambahkan titik penerimaan barang
        for i in range(num_cycles + 1): # +1 untuk siklus terakhir yang mungkin belum selesai
            receive_time = i * t_cycle
            if receive_time <= t_total:
                ax2.scatter(receive_time, eoq + safety_stock, color='green', s=100, zorder=5, edgecolors='black')
                # ax2.annotate('Barang Tiba!', xy=(receive_time, eoq + safety_stock), xytext=(receive_time + t_cycle*0.05, eoq + safety_stock + eoq*0.1),
                #              arrowprops=dict(facecolor='green', shrink=0.05),
                #              horizontalalignment='left', verticalalignment='bottom', fontsize=10, color='green')


    ax2.set_xlabel('Waktu (Hari)')
    ax2.set_ylabel('Jumlah Stok (unit)')
    ax2.set_title('Simulasi Siklus Persediaan', fontsize=16)
    ax2.legend()
    ax2.grid(True, linestyle='-', alpha=0.7)
    ax2.set_ylim(bottom=0)
    st.pyplot(fig2)

    with st.container(border=True):
        st.markdown("**🔍 Penjelasan Grafik Siklus:**")
        st.markdown("""
        Grafik ini menyimulasikan pergerakan tingkat persediaan dari waktu ke waktu.
        - **Garis Biru (Tingkat Persediaan):** Menunjukkan bagaimana stok menurun seiring dengan permintaan harian.
        - **Garis Oranye Putus-putus (ROP):** Ketika tingkat persediaan mencapai garis ini, itu adalah sinyal untuk melakukan pemesanan baru.
        - **Garis Merah Titik-titik (Stok Pengaman):** Ini adalah tingkat stok minimum yang harus dijaga untuk menghindari kehabisan barang jika terjadi variasi permintaan atau keterlambatan pengiriman.
        - **Panah 'Pesan Ulang!':** Menunjukkan titik di mana pesanan baru ditempatkan.
        - **Siklus:** Setelah pesanan tiba (setelah waktu tunggu), tingkat persediaan akan kembali naik ke level maksimum (EOQ + Safety Stock), memulai siklus baru.
        """)

# --- KONTROL TAB UTAMA ---
st.header("Pilih Model Matematika", divider='rainbow')
# Hanya menampilkan satu tab untuk Model Persediaan
tab_eoq = st.tabs(["📦 Model Persediaan"])[0]

with tab_eoq:
    model_persediaan()

# --- FOOTER ---
st.divider()
st.caption("Fauzi Aditya | Marita Andika Putri | Naufal Khoirul Ibrahim | Poppi Marsanti Ramadani")
st.caption("© 2025 Kelompok 9 - Matematika Terapan | Dikembangkan untuk Tugas Kelompok")
