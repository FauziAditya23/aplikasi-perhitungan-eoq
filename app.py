import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd # Import pandas for table display

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

st.set_page_config(layout="wide", page_title="EOQ Simulator", page_icon="�") # Mengatur layout halaman menjadi lebar dan menambahkan ikon/judul

st.title("📦 Simulasi Sistem Persediaan Barang (EOQ Model)")
st.markdown("""
Selamat datang di alat simulasi EOQ interaktif!
Aplikasi ini akan membantu Anda menentukan jumlah pemesanan optimal untuk persediaan barang Anda,
meminimalkan total biaya, dan menganalisis bagaimana perubahan parameter memengaruhi keputusan persediaan Anda.
""")

# Input dari pengguna di sidebar
st.sidebar.header("⚙️ Input Parameter Persediaan")
annual_demand = st.sidebar.number_input("Permintaan Tahunan (D) 📈", min_value=1, value=1000, help="Jumlah total unit yang dibutuhkan dalam setahun.")
# Mengubah nilai default untuk biaya pemesanan dan penyimpanan menjadi jutaan
ordering_cost = st.sidebar.number_input("Biaya Pemesanan (S) (Rp) 💸", min_value=0.01, value=5000000.0, help="Biaya tetap untuk setiap kali melakukan pemesanan dalam Rupiah.")
holding_cost = st.sidebar.number_input("Biaya Penyimpanan (H) (Rp) 🏦", min_value=0.01, value=50000.0, help="Biaya untuk menyimpan satu unit barang selama setahun dalam Rupiah.")

# Perhitungan
if st.sidebar.button("✨ Hitung EOQ dan Analisis"):
    st.subheader("📊 Hasil Utama Perhitungan EOQ Optimal")

    eoq = calculate_eoq(annual_demand, ordering_cost, holding_cost)
    
    # Memanggil fungsi calculate_total_inventory_cost untuk mendapatkan semua komponen biaya
    ordering_cost_at_eoq, holding_cost_at_eoq, total_cost_at_eoq = calculate_total_inventory_cost(annual_demand, ordering_cost, holding_cost, eoq)
    
    orders_per_year_at_eoq = calculate_orders_per_year(annual_demand, eoq)

    # Menampilkan hasil dalam bentuk metrik yang lebih menarik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Economic Order Quantity (EOQ)", f"{eoq:,.2f} unit" if np.isfinite(eoq) else "Tak Terhingga")
        st.caption("Jumlah pesanan optimal untuk meminimalkan total biaya persediaan.")
    with col2:
        st.metric("💰 Total Biaya Persediaan (pada EOQ)", f"Rp {total_cost_at_eoq:,.2f}" if np.isfinite(total_cost_at_eoq) else "Tak Terhingga")
        st.caption("Total biaya yang dikeluarkan jika memesan sejumlah EOQ.")
    with col3:
        st.metric("🔄 Jumlah Pemesanan per Tahun (pada EOQ)", f"{orders_per_year_at_eoq:,.2f} kali" if np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga")
        st.caption("Berapa kali Anda perlu memesan dalam setahun jika memesan sejumlah EOQ.")

    st.markdown("---") # Garis pemisah

    # Bagian input kuantitas pesanan kustom
    st.subheader("🔍 Analisis Kuantitas Pesanan Kustom")
    # Menangani nilai default custom_order_quantity jika EOQ tak terhingga
    default_custom_quantity = int(eoq) if np.isfinite(eoq) and eoq > 0 else annual_demand
    custom_order_quantity = st.number_input("Masukkan Kuantitas Pesanan Kustom (Q_kustom) 🔢", min_value=1, value=default_custom_quantity, help="Masukkan jumlah pesanan yang ingin Anda analisis dan bandingkan.")

    if custom_order_quantity > 0:
        ordering_cost_custom, holding_cost_custom, total_cost_custom = calculate_total_inventory_cost(annual_demand, ordering_cost, holding_cost, custom_order_quantity)
        orders_per_year_custom = calculate_orders_per_year(annual_demand, custom_order_quantity)

        st.write(f"Jika Anda memesan **{custom_order_quantity:,.0f} unit** per pesanan:")
        st.metric("Total Biaya Persediaan Kustom", f"Rp {total_cost_custom:,.2f}" if np.isfinite(total_cost_custom) else "Tak Terhingga")
        st.metric("Jumlah Pemesanan per Tahun Kustom", f"{orders_per_year_custom:,.2f} kali" if np.isfinite(orders_per_year_custom) else "Tak Terhingga")

        if np.isfinite(total_cost_at_eoq) and np.isfinite(total_cost_custom):
            if total_cost_custom > total_cost_at_eoq:
                st.warning(f"⚠️ Total biaya kustom (Rp {total_cost_custom:,.2f}) lebih tinggi dari total biaya pada EOQ (Rp {total_cost_at_eoq:,.2f}).")
            elif total_cost_custom < total_cost_at_eoq:
                st.success(f"✅ Total biaya kustom (Rp {total_cost_custom:,.2f}) lebih rendah dari total biaya pada EOQ (Rp {total_cost_at_eoq:,.2f}). Ini mungkin karena pembulatan atau nilai yang sangat dekat.")
            else:
                st.info("ℹ️ Total biaya kustom sama dengan total biaya pada EOQ.")
        elif np.isfinite(total_cost_custom) and not np.isfinite(total_cost_at_eoq):
             st.success(f"✅ Total biaya kustom (Rp {total_cost_custom:,.2f}) adalah nilai yang terhingga, sedangkan EOQ memiliki biaya tak terhingga.")
        elif not np.isfinite(total_cost_custom) and np.isfinite(total_cost_at_eoq):
             st.warning(f"⚠️ Total biaya kustom adalah tak terhingga, sedangkan EOQ memiliki biaya terhingga (Rp {total_cost_at_eoq:,.2f}).")
        else:
             st.info("ℹ️ Baik total biaya kustom maupun total biaya pada EOQ adalah tak terhingga.")


    st.markdown("---") # Garis pemisah

    st.subheader("📋 Ringkasan Hasil")
    summary_data = {
        "Metrik": ["Economic Order Quantity (EOQ)", "Total Biaya Persediaan (pada EOQ)", "Jumlah Pemesanan per Tahun (pada EOQ)"],
        "Nilai": [
            f"{eoq:,.2f} unit" if np.isfinite(eoq) else "Tak Terhingga",
            f"Rp {total_cost_at_eoq:,.2f}" if np.isfinite(total_cost_at_eoq) else "Tak Terhingga",
            f"{orders_per_year_at_eoq:,.2f} kali" if np.isfinite(orders_per_year_at_eoq) else "Tak Terhingga"
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
        * $S$ = Biaya Pemesanan = Rp {ordering_cost:,.2f}
        * $H$ = Biaya Penyimpanan = Rp {holding_cost:,.2f}
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
                \text{{Biaya Pemesanan}} = \left(\frac{{{annual_demand}}}{{{eoq:,.2f}}}\right) \times \text{{Rp }} {ordering_cost:,.2f}
            ''')
            st.latex(fr'''
                \text{{Biaya Pemesanan}} = \text{{Rp }} { (annual_demand / eoq) * ordering_cost:,.2f}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = \left(\frac{{{eoq:,.2f}}}{{2}}\right) \times \text{{Rp }} {holding_cost:,.2f}
            ''')
            st.latex(fr'''
                \text{{Biaya Penyimpanan}} = \text{{Rp }} { (eoq / 2) * holding_cost:,.2f}
            ''')
            st.latex(fr'''
                \text{{Total Biaya}} = \text{{Rp }} {ordering_cost_at_eoq:,.2f} + \text{{Rp }} {holding_cost_at_eoq:,.2f}
            ''')
            st.latex(fr'''
                \text{{Total Biaya}} = \text{{Rp }} {total_cost_at_eoq:,.2f}
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

    st.markdown("---") # Garis pemisah

    st.subheader("📈 Visualisasi Biaya Persediaan")

    # Buat rentang kuantitas pesanan untuk grafik
    # Pastikan rentang mencakup EOQ dan kuantitas kustom, dan selalu terhingga
    max_q_value = annual_demand * 2 # Base value
    if np.isfinite(eoq) and eoq > 0:
        max_q_value = max(max_q_value, eoq * 1.5)
    if np.isfinite(custom_order_quantity) and custom_order_quantity > 0:
        max_q_value = max(max_q_value, custom_order_quantity * 1.5)
    
    # Pastikan min_value untuk linspace adalah setidaknya 1 untuk menghindari masalah
    q_values = np.linspace(1, max_q_value, 500)
    
    ordering_costs_plot = [(annual_demand / q) * ordering_cost for q in q_values]
    holding_costs_plot = [(q / 2) * holding_cost for q in q_values]
    total_costs_plot = [oc + hc for oc, hc in zip(ordering_costs_plot, holding_costs_plot)]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(q_values, ordering_costs_plot, label="Biaya Pemesanan", color='#FF6347') # Tomato
    ax.plot(q_values, holding_costs_plot, label="Biaya Penyimpanan", color='#4682B4') # SteelBlue
    ax.plot(q_values, total_costs_plot, label="Total Biaya Persediaan", color='#32CD32', linewidth=2) # LimeGreen
    
    if np.isfinite(eoq) and eoq > 0:
        ax.axvline(eoq, color='#8A2BE2', linestyle='--', label=f'EOQ: {eoq:,.2f}') # BlueViolet
    if np.isfinite(custom_order_quantity) and custom_order_quantity > 0:
        ax.axvline(custom_order_quantity, color='#FFD700', linestyle=':', label=f'Kuantitas Kustom: {custom_order_quantity:,.0f}') # Gold
    
    ax.set_xlabel("Kuantitas Pesanan (Q)")
    ax.set_ylabel("Biaya (Rp)") # Menambahkan (Rp) pada label sumbu Y
    ax.set_title("Grafik Biaya Persediaan vs. Kuantitas Pesanan")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_ylim(bottom=0) # Memastikan sumbu y dimulai dari 0
    st.pyplot(fig)

    st.markdown("""
    **Penjelasan Grafik:**
    * **Garis Merah (Biaya Pemesanan):** Menurun seiring bertambahnya kuantitas pesanan, karena Anda memesan lebih jarang.
    * **Garis Biru (Biaya Penyimpanan):** Meningkat seiring bertambahnya kuantitas pesanan, karena Anda menyimpan lebih banyak persediaan.
    * **Garis Hijau (Total Biaya Persediaan):** Menunjukkan jumlah dari biaya pemesanan dan biaya penyimpanan. Titik terendah pada garis ini adalah EOQ.
    * **Garis Ungu Putus-putus (EOQ):** Menunjukkan kuantitas pesanan optimal di mana total biaya persediaan berada pada titik terendah. (Hanya ditampilkan jika EOQ terhingga)
    * **Garis Oranye Titik-titik (Kuantitas Kustom):** Menunjukkan posisi kuantitas pesanan kustom Anda pada grafik. (Hanya ditampilkan jika kuantitas kustom terhingga)
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
            sensitivity_data_D.append({"Permintaan (D)": f"{d_var:,.0f}", "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": f"Rp {total_cost_var:,.2f}" if np.isfinite(total_cost_var) else "Tak Terhingga"})
        df_sensitivity_D = pd.DataFrame(sensitivity_data_D)
        st.dataframe(df_sensitivity_D)

        st.markdown("#### Sensitivitas terhadap Biaya Pemesanan (S)")
        ordering_cost_variations = np.linspace(ordering_cost * 0.5, ordering_cost * 1.5, 10)
        sensitivity_data_S = []
        for s_var in ordering_cost_variations:
            eoq_var = calculate_eoq(annual_demand, s_var, holding_cost)
            _, _, total_cost_var = calculate_total_inventory_cost(annual_demand, s_var, holding_cost, eoq_var)
            sensitivity_data_S.append({"Biaya Pemesanan (S)": f"Rp {s_var:,.2f}", "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": f"Rp {total_cost_var:,.2f}" if np.isfinite(total_cost_var) else "Tak Terhingga"})
        df_sensitivity_S = pd.DataFrame(sensitivity_data_S)
        st.dataframe(df_sensitivity_S)

        st.markdown("#### Sensitivitas terhadap Biaya Penyimpanan (H)")
        holding_cost_variations = np.linspace(holding_cost * 0.5, holding_cost * 1.5, 10)
        sensitivity_data_H = []
        for h_var in holding_cost_variations:
            if h_var > 0: # Pastikan biaya penyimpanan tidak nol untuk perhitungan EOQ
                eoq_var = calculate_eoq(annual_demand, ordering_cost, h_var)
                _, _, total_cost_var = calculate_total_inventory_cost(annual_demand, ordering_cost, h_var, eoq_var)
                sensitivity_data_H.append({"Biaya Penyimpanan (H)": f"Rp {h_var:,.2f}", "EOQ": f"{eoq_var:,.2f}" if np.isfinite(eoq_var) else "Tak Terhingga", "Total Biaya": f"Rp {total_cost_var:,.2f}" if np.isfinite(total_cost_var) else "Tak Terhingga"})
            else:
                sensitivity_data_H.append({"Biaya Penyimpanan (H)": f"Rp {h_var:,.2f}", "EOQ": "Tak Terhingga", "Total Biaya": "Tak Terhingga"})
        df_sensitivity_H = pd.DataFrame(sensitivity_data_H)
        st.dataframe(df_sensitivity_H)

    st.markdown("---") # Garis pemisah
    st.markdown("Made with ❤️ using Streamlit.")
