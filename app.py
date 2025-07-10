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

def calculate_safety_stock(z_score, std_dev_daily_demand, lead_time_days):
    """
    Menghitung Safety Stock (Persediaan Pengaman).
    z_score: Nilai Z yang sesuai dengan tingkat layanan
    std_dev_daily_demand: Standar deviasi permintaan harian
    lead_time_days: Waktu tunggu dalam hari
    """
    if lead_time_days <= 0 or std_dev_daily_demand < 0:
        return 0 # Tidak ada safety stock jika lead time nol atau std dev negatif
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
        return 0 # Tidak ada reorder point jika lead time atau avg daily demand negatif
    reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
    return reorder_point

st.set_page_config(layout="wide", page_title="EOQ & Inventory Model Simulator", page_icon="📈")

st.title("📦 Simulasi Sistem Persediaan Barang (EOQ & ROP Model)")
st.markdown("""
Aplikasi ini akan membantu Anda menentukan jumlah pemesanan optimal (EOQ), titik pemesanan kembali (ROP),
dan persediaan pengaman (Safety Stock) untuk meminimalkan total biaya persediaan Anda
sambil menjaga tingkat layanan yang diinginkan.
""")

# Input dari pengguna di sidebar
st.sidebar.header("⚙️ Input Parameter Persediaan")
annual_demand = st.sidebar.number_input("Permintaan Tahunan (D) 📈", min_value=1, value=5000, help="Jumlah total unit yang dibutuhkan dalam setahun.")
ordering_cost = st.sidebar.number_input("Biaya Pemesanan (S) (Rp) 💸", min_value=1, value=100000, help="Biaya tetap untuk setiap kali melakukan pemesanan dalam Rupiah.")
holding_cost = st.sidebar.number_input("Biaya Penyimpanan (H) (Rp) 🏦", min_value=1, value=500, help="Biaya untuk menyimpan satu unit barang selama setahun dalam Rupiah.")

st.sidebar.markdown("---")
st.sidebar.header("🛡️ Parameter Safety Stock & ROP")
lead_time_days = st.sidebar.number_input("Waktu Tunggu (Lead Time) (hari) ⏳", min_value=0, value=14, help="Jumlah hari antara pemesanan dan penerimaan barang.")
service_level_percent = st.sidebar.slider("Tingkat Layanan (Service Level) (%) 🎯", min_value=50, max_value=99, value=95, help="Probabilitas tidak terjadi kekurangan stok selama waktu tunggu.")
std_dev_daily_demand = st.sidebar.number_input("Standar Deviasi Permintaan Harian (unit) 📉", min_value=0.0, value=5.0, help="Variabilitas permintaan harian. Jika tidak tahu, coba estimasi.")


# Perhitungan
if st.sidebar.button("✨ Hitung EOQ dan Analisis"):
    st.subheader("📊 Hasil Utama Perhitungan EOQ Optimal")

    eoq = calculate_eoq(annual_demand, ordering_cost, holding_cost)
    
    ordering_cost_at_eoq, holding_cost_at_eoq, total_cost_at_eoq = calculate_total_inventory_cost(annual_demand, ordering_cost, holding_cost, eoq)
    orders_per_year_at_eoq = calculate_orders_per_year(annual_demand, eoq)

    # Perhitungan ROP dan Safety Stock
    avg_daily_demand = annual_demand / 365.0
    z_score = norm.ppf(service_level_percent / 100.0) # Menggunakan scipy untuk Z-score
    
    safety_stock = calculate_safety_stock(z_score, std_dev_daily_demand, lead_time_days)
    reorder_point = calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock)


    # Menampilkan hasil dalam bentuk metrik yang lebih menarik
    col1_res, col2_res, col3_res = st.columns(3)
    with col1_res:
        st.metric("📦 Economic Order Quantity (EOQ)", f"{eoq:,.2f} unit" if np.isfinite(eoq) else "Tak Terhingga")
        st.caption("Jumlah pesanan optimal yang meminimalkan total biaya.")
    with col2_res:
        st.metric("💰 Total Biaya Persediaan (pada EOQ)", format_rupiah(total_cost_at_eoq))
        st.caption("Total biaya yang dikeluarkan jika memesan sejumlah EOQ.")
    with col3_res:
        st.metric("🔄 Jumlah Pemesanan per Tahun (pada EOQ)", f"{orders_per_year_at_eoq:,.2f} kali" if np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga")
        st.caption("Frekuensi pemesanan dalam setahun.")

    st.markdown("---") # Garis pemisah

    st.subheader("🛡️ Hasil Perhitungan Safety Stock & Reorder Point")
    col_ss, col_rop = st.columns(2)
    with col_ss:
        st.metric("🛡️ Safety Stock (Persediaan Pengaman)", f"{safety_stock:,.2f} unit")
        st.caption("Persediaan ekstra untuk melindungi dari variabilitas permintaan atau waktu tunggu.")
    with col_rop:
        st.metric("🔔 Reorder Point (Titik Pemesanan Kembali)", f"{reorder_point:,.2f} unit")
        st.caption("Tingkat persediaan di mana pesanan baru harus dilakukan.")
    
    st.markdown("---") # Garis pemisah

    # Bagian input kuantitas pesanan kustom
    st.subheader("🔍 Analisis Kuantitas Pesanan Kustom")
    default_custom_quantity = int(eoq) if np.isfinite(eoq) and eoq > 0 else annual_demand
    custom_order_quantity = st.number_input("Masukkan Kuantitas Pesanan Kustom (Q_kustom) 🔢", min_value=1, value=default_custom_quantity, help="Masukkan jumlah pesanan yang ingin Anda analisis dan bandingkan.")

    if custom_order_quantity > 0:
        ordering_cost_custom, holding_cost_custom, total_cost_custom = calculate_total_inventory_cost(annual_demand, ordering_cost, holding_cost, custom_order_quantity)
        orders_per_year_custom = calculate_orders_per_year(annual_demand, custom_order_quantity)

        st.write(f"Jika Anda memesan **{custom_order_quantity:,.0f} unit** per pesanan:")
        st.metric("Total Biaya Persediaan Kustom", format_rupiah(total_cost_custom))
        st.metric("Jumlah Pemesanan per Tahun Kustom", f"{orders_per_year_custom:,.2f} kali" if np.isfinite(orders_per_year_custom) else "Tak Terhingga")

        if np.isfinite(total_cost_at_eoq) and np.isfinite(total_cost_custom):
            if total_cost_custom > total_cost_at_eoq:
                st.warning(f"⚠️ Total biaya kustom ({format_rupiah(total_cost_custom)}) lebih tinggi dari total biaya pada EOQ ({format_rupiah(total_cost_at_eoq)}).")
            elif total_cost_custom < total_cost_at_eoq:
                st.success(f"✅ Total biaya kustom ({format_rupiah(total_cost_custom)}) lebih rendah dari total biaya pada EOQ ({format_rupiah(total_cost_at_eoq)}). Ini mungkin karena pembulatan atau nilai yang sangat dekat.")
            else:
                st.info("ℹ️ Total biaya kustom sama dengan total biaya pada EOQ.")
        elif np.isfinite(total_cost_custom) and not np.isfinite(total_cost_at_eoq):
            st.success(f"✅ Total biaya kustom ({format_rupiah(total_cost_custom)}) adalah nilai yang terhingga, sedangkan EOQ memiliki biaya tak terhingga.")
        elif not np.isfinite(total_cost_custom) and np.isfinite(total_cost_at_eoq):
            st.warning(f"⚠️ Total biaya kustom adalah tak terhingga, sedangkan EOQ memiliki biaya terhingga ({format_rupiah(total_cost_at_eoq)}).")
        else:
            st.info("ℹ️ Baik total biaya kustom maupun total biaya pada EOQ adalah tak terhingga.")


    st.markdown("---") # Garis pemisah

    st.subheader("📋 Ringkasan Hasil")
    summary_data = {
        "Metrik": ["Economic Order Quantity (EOQ)", "Total Biaya Persediaan (pada EOQ)", "Jumlah Pemesanan per Tahun (pada EOQ)", "Safety Stock (Persediaan Pengaman)", "Reorder Point (Titik Pemesanan Kembali)"],
        "Nilai": [
            f"{eoq:,.2f} unit" if np.isfinite(eoq) else "Tak Terhingga",
            format_rupiah(total_cost_at_eoq),
            f"{orders_per_year_at_eoq:,.2f} kali" if np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga",
            f"{safety_stock:,.2f} unit",
            f"{reorder_point:,.2f} unit"
        ]
    }
    df_summary = pd.DataFrame(summary_data)
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
        * $D$ = Permintaan Tahunan = {annual_demand} unit
        * $S$ = Biaya Pemesanan = {format_rupiah(ordering_cost)}
        * $H$ = Biaya Penyimpanan = {format_rupiah(holding_cost)}
        """)
        st.latex(fr'''
            EOQ = \sqrt{{\frac{{2 \times {annual_demand} \times {ordering_cost:,.2f}}}{{{holding_cost:,.2f}}}}}
        ''')
        st.latex(fr'''
            EOQ = \sqrt{{\frac{{{2 * annual_demand * ordering_cost:,.2f}}}{{{holding_cost:,.2f}}}}}
        ''')
        if holding_cost > 0:
            st.latex(fr'''
                EOQ = \sqrt{{{ (2 * annual_demand * ordering_cost) / holding_cost:,.2f}}}
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
                \text{{Biaya Pemesanan}} = \left(\frac{{{annual_demand}}}{{{eoq:,.2f}}}\right) \times {format_rupiah(ordering_cost).replace('Rp ', '')}
            ''')
            st.latex(fr'''
                \text{{Biaya Pemesanan}} = {format_rupiah((annual_demand / eoq) * ordering_cost)}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = \left(\frac{{{eoq:,.2f}}}{{2}}\right) \times {format_rupiah(holding_cost).replace('Rp ', '')}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = {format_rupiah((eoq / 2) * holding_cost)}
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
                \text{{Jumlah Pemesanan per Tahun}} = \frac{{{annual_demand}}}{{{eoq:,.2f}}}
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
            \text{{Rata-rata Permintaan Harian}} = \frac{{{annual_demand}}}{{365}} = {avg_daily_demand:,.2f} \text{{ unit/hari}}
        ''')
        st.latex(r'''
            Z\text{-score} = \text{Nilai dari distribusi normal standar}
        ''')
        st.markdown(f"Untuk tingkat layanan {service_level_percent}%, Z-score adalah sekitar {z_score:,.2f}.")
        st.latex(fr'''\text{{Z-score}} = {z_score:,.2f}''') # Corrected line
        st.latex(r'''
            \text{Safety Stock} = Z\text{-score} \times \text{Std Dev Permintaan Harian} \times \sqrt{\text{Waktu Tunggu (hari)}}
        ''')
        st.markdown(f"""
        Di mana:
        * $\text{{Z-score}} = {z_score:,.2f}$
        * $\text{{Std Dev Permintaan Harian}}$ = {std_dev_daily_demand:,.2f} unit
        * $\text{{Waktu Tunggu}}$ = {lead_time_days} hari
        """)
        st.latex(fr'''
            \text{{Safety Stock}} = {z_score:,.2f} \times {std_dev_daily_demand:,.2f} \times \sqrt{{{lead_time_days}}}
        ''')
        if lead_time_days > 0:
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
    min_q_plot = 1 # Minimum order quantity for the plot
    if np.isfinite(eoq) and eoq > 0:
        # Set max_q_value to be around 2.5 times EOQ to show the curve clearly
        # But also ensure it's at least 1.5 times the custom quantity if that's larger
        max_q_value_base = eoq * 2.5
    else:
        # If EOQ is infinite or zero, base it on annual demand or a fixed large value
        max_q_value_base = annual_demand * 0.5 if annual_demand > 0 else 1000

    # custom_order_quantity is not defined here yet, so we need to ensure it's handled.
    # For plotting purposes, we can assume a default or use the calculated EOQ for scaling
    # if a custom quantity isn't explicitly set before the plot generation.
    # However, the custom_order_quantity input is *after* this block.
    # So, we'll use a placeholder for custom_order_quantity for plot scaling if needed,
    # or rely on the default set in the custom quantity input later.
    # For now, let's ensure the plot scales well around EOQ.

    # Ensure a reasonable upper bound for the plot, not excessively large
    max_q_plot = max(50, int(max_q_value_base)) # Ensure it's at least 50 units for a visible curve

    q_values = np.linspace(min_q_plot, max_q_plot, 500)

    # Filter out non-positive or non-finite q_values if any, though linspace should handle this if min_q_plot is > 0
    q_values = q_values[q_values > 0]
    if not np.any(q_values): # Handle case where q_values might become empty after filtering
        st.warning("Tidak dapat membuat plot biaya karena rentang kuantitas pesanan tidak valid.")
    else:
        holding_costs_plot = [(q / 2) * holding_cost for q in q_values]
        ordering_costs_plot = [(annual_demand / q) * ordering_cost for q in q_values]
        total_costs_plot = [oc + hc for oc, hc in zip(ordering_costs_plot, holding_costs_plot)]

        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Reorder plot calls to match the desired legend order: Biaya Penyimpanan, Biaya Pemesanan, Total Biaya
        ax.plot(q_values, holding_costs_plot, label="Biaya Penyimpanan", color='blue') # Blue for Holding Cost
        ax.plot(q_values, ordering_costs_plot, label="Biaya Pemesanan", color='green') # Green for Ordering Cost
        ax.plot(q_values, total_costs_plot, label="Total Biaya", color='red', linewidth=2) # Red for Total Cost

        if np.isfinite(eoq) and eoq > 0:
            ax.axvline(eoq, color='purple', linestyle='--', label=f'EOQ: {eoq:,.2f} unit') # Purple dashed line for EOQ
            # Add annotation for lowest cost point
            if np.isfinite(total_cost_at_eoq):
                ax.annotate(f'Biaya Terendah\n{format_rupiah(total_cost_at_eoq)}',
                            xy=(eoq, total_cost_at_eoq),
                            # Adjust xytext and arrowprops for better positioning and appearance
                            xytext=(eoq + max_q_plot * 0.05, total_cost_at_eoq + total_cost_at_eoq * 0.1),
                            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8, headlength=8),
                            horizontalalignment='left', verticalalignment='bottom',
                            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.5, alpha=0.9))
        
        # custom_order_quantity is defined AFTER this plot, so it cannot be used here directly for plotting
        # if np.isfinite(custom_order_quantity) and custom_order_quantity > 0:
        #     # Check if custom_order_quantity is within the plot's x-limits to avoid drawing outside
        #     if custom_order_quantity >= min_q_plot and custom_order_quantity <= max_q_plot:
        #         ax.axvline(custom_order_quantity, color='#FFD700', linestyle=':', label=f'Kuantitas Kustom: {custom_order_quantity:,.0f} unit') # Gold
        
        ax.set_xlabel("Kuantitas Pemesanan (unit)")
        ax.set_ylabel("Biaya Tahunan (Rp)")
        ax.set_title("Analisis Biaya Persediaan (EOQ)", fontsize=16)
        ax.legend()
        ax.grid(True, linestyle='-', alpha=0.7)
        ax.set_ylim(bottom=0)
        ax.set_xlim(left=min_q_plot)
        st.pyplot(fig)

        st.markdown("""
        **Penjelasan Grafik:**
        * **Garis Biru (Biaya Penyimpanan):** Meningkat seiring bertambahnya kuantitas pesanan, karena Anda menyimpan lebih banyak persediaan.
        * **Garis Hijau (Biaya Pemesanan):** Menurun seiring bertambahnya kuantitas pesanan, karena Anda memesan lebih jarang.
        * **Garis Merah (Total Biaya):** Menunjukkan jumlah dari biaya pemesanan dan biaya penyimpanan. Titik terendah pada garis ini adalah EOQ.
        * **Garis Ungu Putus-putus (EOQ):** Menunjukkan kuantitas pesanan optimal di mana total biaya persediaan berada pada titik terendah. (Hanya ditampilkan jika EOQ terhingga)
        * **Anotasi Biaya Terendah:** Menunjukkan titik biaya total minimum pada EOQ.
        """)

    st.markdown("---") # Garis pemisah

    # Menggunakan expander untuk analisis sensitivitas
    with st.expander("🔬 Lakukan Analisis Sensitivitas"):
        st.write("Lihat bagaimana EOQ dan biaya total berubah jika salah satu parameter bervariasi.")

        st.markdown("#### Sensitivitas terhadap Permintaan Tahunan (D)")
        demand_variations = np.linspace(annual_demand * 0.5, annual_demand * 1.5, 10)
        sensitivity_data_D = []
        for d_var in demand_variations:
            eoq_var = calculate_eoq(d_var, ordering_cost, holding_cost)
            _, _, total_cost_var = calculate_total_inventory_cost(d_var, ordering_cost, holding_cost, eoq_var)
            sensitivity_data_D.append({"Permintaan (D)": f"{d_var:,.0f}", "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": format_rupiah(total_cost_var)})
        df_sensitivity_D = pd.DataFrame(sensitivity_data_D)
        st.dataframe(df_sensitivity_D)

        st.markdown("#### Sensitivitas terhadap Biaya Pemesanan (S)")
        ordering_cost_variations = np.linspace(ordering_cost * 0.5, ordering_cost * 1.5, 10)
        sensitivity_data_S = []
        for s_var in ordering_cost_variations:
            eoq_var = calculate_eoq(annual_demand, s_var, holding_cost)
            _, _, total_cost_var = calculate_total_inventory_cost(annual_demand, s_var, holding_cost, eoq_var)
            sensitivity_data_S.append({"Biaya Pemesanan (S)": format_rupiah(s_var), "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": format_rupiah(total_cost_var)})
        df_sensitivity_S = pd.DataFrame(sensitivity_data_S)
        st.dataframe(df_sensitivity_S)

        st.markdown("#### Sensitivitas terhadap Biaya Penyimpanan (H)")
        holding_cost_variations = np.linspace(holding_cost * 0.5, holding_cost * 1.5, 10)
        sensitivity_data_H = []
        for h_var in holding_cost_variations:
            if h_var > 0: # Pastikan biaya penyimpanan tidak nol untuk perhitungan EOQ
                eoq_var = calculate_eoq(annual_demand, ordering_cost, h_var)
                _, _, total_cost_var = calculate_total_inventory_cost(annual_demand, ordering_cost, h_var, eoq_var)
                sensitivity_data_H.append({"Biaya Penyimpanan (H)": format_rupiah(h_var), "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": format_rupiah(total_cost_var)})
            else:
                sensitivity_data_H.append({"Biaya Penyimpanan (H)": format_rupiah(h_var), "EOQ": "Tak Terhingga", "Total Biaya": "Tak Terhingga"})
        df_sensitivity_H = pd.DataFrame(sensitivity_data_H)
        st.dataframe(df_sensitivity_H)

    st.markdown("---") # Garis pemisah
    st.markdown("Made with ❤️ using Streamlit.")
