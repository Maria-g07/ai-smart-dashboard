# ==========================================
# 1. ΕΙΣΑΓΩΓΗ ΒΙΒΛΙΟΘΗΚΩΝ (LIBRARIES)
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 2. ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ & CUSTOM UI STYLING
# ==========================================
st.set_page_config(
    page_title="AI Smart Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS για επαγγελματική αισθητική (Enterprise Look & Feel)
st.markdown("""
    <style>
    /* Βελτίωση εμφάνισης καρτών και κειμένων */
    .stMetric {
        background-color: rgba(28, 131, 246, 0.05);
        border: 1px solid rgba(28, 131, 246, 0.2);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ΤΙΤΛΟΣ ΚΑΙ ΕΙΣΑΓΩΓΙΚΟ ΚΕΙΜΕΝΟ
# ==========================================
st.title("📊 AI Smart Sales Dashboard (Enterprise Edition)")
st.markdown("Επαγγελματικό Dashboard Λιανικής με 3ετή Δεδομένα, Tabs, Custom UI Styling και AI Intelligence.")


# ==========================================
# 4. ΣΥΝΑΡΤΗΣΗ ΦΟΡΤΩΣΗΣ ΠΡΑΓΜΑΤΙΚΩΝ ΔΕΔΟΜΕΝΩΝ (OPEN-SOURCE SUPERSTORE)
# ==========================================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv"
    data_frame = pd.read_csv(url, encoding='latin1')
    data_frame.columns = data_frame.columns.str.lower().str.strip()

    # Αντιστοίχιση βασικών στηλών
    data_frame['Date'] = pd.to_datetime(
        data_frame['order date'] if 'order date' in data_frame.columns else data_frame.columns[0])
    data_frame['Sales'] = pd.to_numeric(data_frame['sales'] if 'sales' in data_frame.columns else 100)
    data_frame['Profit'] = pd.to_numeric(
        data_frame['profit'] if 'profit' in data_frame.columns else data_frame['Sales'] * 0.2)
    data_frame['Cost'] = data_frame['Sales'] - data_frame['Profit']
    data_frame['Units'] = pd.to_numeric(data_frame['order quantity'] if 'order quantity' in data_frame.columns else 1)
    data_frame['Region'] = data_frame['region'] if 'region' in data_frame.columns else 'Global'
    data_frame['Category'] = data_frame['product category'] if 'product category' in data_frame.columns else 'General'
    data_frame['Product'] = data_frame['product name'] if 'product name' in data_frame.columns else 'Item'

    # Προσθήκη Segment και Πολιτείας
    data_frame['Segment'] = data_frame['segment'] if 'segment' in data_frame.columns else 'Consumer'
    data_frame['State'] = data_frame['state'] if 'state' in data_frame.columns else 'California'

    # Συντεταγμένες για τον γεωγραφικό χάρτη
    state_coords = {
        'California': (36.7783, -119.4179), 'New York': (40.7128, -74.0060),
        'Texas': (31.9686, -99.9018), 'Washington': (47.7511, -120.7401),
        'Illinois': (40.3363, -89.0022), 'Pennsylvania': (41.2033, -77.1945)
    }
    data_frame['Lat'] = data_frame['State'].map(lambda x: state_coords.get(x, (37.0902, -95.7129))[0])
    data_frame['Lon'] = data_frame['State'].map(lambda x: state_coords.get(x, (37.0902, -95.7129))[1])

    return data_frame[
        ['Date', 'Region', 'Category', 'Product', 'Segment', 'State', 'Lat', 'Lon', 'Sales', 'Cost', 'Profit', 'Units']]


df = load_data()

# ==========================================
# 5. ΡΥΘΜΙΣΕΙΣ, ΦΙΛΤΡΑ & DATE RANGE ΣΤΗΝ ΠΛΕΥΡΙΚΗ ΜΠΑΡΑ
# ==========================================
st.sidebar.header("⚙️ Ρυθμίσεις & Θέμα")

theme_mode = st.sidebar.radio(
    "Επιλογή Θέματος (Theme):",
    options=["Light Mode ☀️", "Dark Mode 🌙"],
    index=0
)
plotly_template = "plotly_dark" if "Dark" in theme_mode else "plotly_white"

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Χρονικό Εύρος (Date Range)")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Επιλέξτε Περίοδο Ανάλυσης:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Φίλτρα Αναζήτησης")

region_filter = st.sidebar.multiselect(
    "Επιλέξτε Περιοχή (Region):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

category_filter = st.sidebar.multiselect(
    "Επιλέξτε Κατηγορία:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

segment_filter = st.sidebar.multiselect(
    "Επιλέξτε Τμήμα Πελάτη (Segment):",
    options=df["Segment"].unique(),
    default=df["Segment"].unique()
)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Χρονική Ομαδοποίηση")
time_period = st.sidebar.selectbox(
    "Ομαδοποίηση Χρόνου:",
    options=["Ημέρα (Daily)", "Εβδομάδα (Weekly)", "Μήνας (Monthly)", "Έτος (Yearly)"],
    index=2
)

# Εφαρμογή όλων των φίλτρων
filtered_df = df[
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date) &
    (df["Region"].isin(region_filter)) &
    (df["Category"].isin(category_filter)) &
    (df["Segment"].isin(segment_filter))
    ]

# ==========================================
# 6. 🤖 AI CHATBOT / ASSISTANT (SIDEBAR CHAT)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("💬 AI Assistant (Ask Your Data)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.sidebar.chat_message(message["role"]):
        st.write(message["content"])

user_query = st.sidebar.chat_input("Ρωτήστε το AI για τα δεδομένα...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.sidebar.chat_message("user"):
        st.write(user_query)

    query_lower = user_query.lower()
    response = ""

    valid_keywords = [
        "κορυφαί", "καλύτερ", "best", "προϊόν", "product", "περιοχ", "region",
        "κατηγορ", "category", "σύνολ", "πωλήσει", "total", "κέρδ", "profit",
        "μονάδ", "units", "πελάτ", "segment", "ποσοστ", "απόδοσ"
    ]

    is_relevant = any(keyword in query_lower for keyword in valid_keywords)

    if not is_relevant:
        response = (
            "🤖 Ως AI Sales Assistant, απαντώ αποκλειστικά σε ερωτήσεις "
            "σχετικές με τις πωλήσεις, τα κέρδη, τους πελάτες και τα προϊόντα."
        )
    else:
        if "κορυφαί" in query_lower or "καλύτερ" in query_lower or "best" in query_lower:
            if "προϊόν" in query_lower or "product" in query_lower:
                top_p = filtered_df.groupby("Product")["Sales"].sum().idxmax()
                top_p_val = filtered_df.groupby("Product")["Sales"].sum().max()
                response = f"🏆 Το κορυφαίο προϊόν σε πωλήσεις είναι το **{top_p}** με συνολικό τζίρο **${top_p_val:,.0f}**."
            elif "πελάτ" in query_lower or "segment" in query_lower:
                top_s = filtered_df.groupby("Segment")["Sales"].sum().idxmax()
                top_s_val = filtered_df.groupby("Segment")["Sales"].sum().max()
                response = f"👥 Το κορυφαίο τμήμα πελατών είναι το **{top_s}** με συνολικές πωλήσεις **${top_s_val:,.0f}**."
            else:
                top_r = filtered_df.groupby("Region")["Sales"].sum().idxmax()
                top_r_val = filtered_df.groupby("Region")["Sales"].sum().max()
                response = f"🌍 Η κορυφαία περιοχή είναι η **{top_r}** με **${top_r_val:,.0f}** σε πωλήσεις."

        elif "σύνολ" in query_lower or "πωλήσει" in query_lower or "total" in query_lower:
            tot_s = filtered_df["Sales"].sum()
            tot_p = filtered_df["Profit"].sum()
            response = f"💰 Οι συνολικές πωλήσεις ανέρχονται σε **${tot_s:,.0f}** και το καθαρό κέρδος σε **${tot_p:,.0f}**."

        elif "κέρδ" in query_lower or "profit" in query_lower:
            tot_s = filtered_df["Sales"].sum()
            tot_p = filtered_df["Profit"].sum()
            margin = (tot_p / tot_s * 100) if tot_s > 0 else 0
            response = f"💎 Το συνολικό καθαρό κέρδος είναι **${tot_p:,.0f}** (περιθώριο κέρδους **{margin:.1f}%**)."

        else:
            response = f"🤖 Με βάση τα τρέχοντα φίλτρα, έχουμε καταγράψει **{len(filtered_df)}** συναλλαγές με συνολικό τζίρο **${filtered_df['Sales'].sum():,.0f}**."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.sidebar.chat_message("assistant"):
        st.write(response)

# ==========================================
# 7. ΕΛΕΓΧΟΣ ΔΕΔΟΜΕΝΩΝ & ΣΥΓΚΡΙΣΗ ΠΕΡΙΟΔΟΥ (PoP)
# ==========================================
if filtered_df.empty:
    st.warning(
        "⚠️ Δεν βρέθηκαν δεδομένα για τα επιλεγμένα φίλτρα/ημερομηνίες. Παρακαλώ διευρύνετε το χρονικό εύρος ή τα φίλτρα.")
else:
    filtered_df = filtered_df.sort_values('Date')
    mid_index = len(filtered_df) // 2

    prev_period_df = filtered_df.iloc[:mid_index] if mid_index > 0 else filtered_df
    curr_period_df = filtered_df.iloc[mid_index:] if mid_index > 0 else filtered_df

    curr_sales = curr_period_df["Sales"].sum()
    prev_sales = prev_period_df["Sales"].sum()
    sales_pct_change = ((curr_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0.0

    curr_profit = curr_period_df["Profit"].sum()
    prev_profit = prev_period_df["Profit"].sum()
    profit_pct_change = ((curr_profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0.0

    curr_units = int(curr_period_df["Units"].sum())
    prev_units = int(prev_period_df["Units"].sum())
    units_pct_change = ((curr_units - prev_units) / prev_units * 100) if prev_units > 0 else 0.0

    # ==========================================
    # 8. ΔΟΜΗΣΗ ΣΕ 2 ΕΞΥΠΝΕΣ ΚΑΡΤΕΛΕΣ (TABS)
    # ==========================================
    tab1, tab2 = st.tabs([
        "📈 Επισκόπηση & Βασικοί Δείκτες",
        "🔮 AI Αναλύσεις & Προβλέψεις"
    ])

    # ==========================================
    # ΚΑΡΤΕΛΑ 1: ΕΠΙΣΚΟΠΗΣΗ & ΒΑΣΙΚΟΙ ΔΕΙΚΤΕΣ
    # ==========================================
    with tab1:
        st.markdown("### 📈 Βασικοί Δείκτες Απόδοσης & Σύγκριση Περιόδου (PoP)")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="💰 Συνολικές Πωλήσεις", value=f"${curr_sales:,.0f}",
                      delta=f"{sales_pct_change:+.1f}% vs προηγ.")
        with col2:
            st.metric(label="💎 Συνολικό Κέρδος", value=f"${curr_profit:,.0f}",
                      delta=f"{profit_pct_change:+.1f}% vs προηγ.")
        with col3:
            st.metric(label="📦 Πωληθείσες Μονάδες", value=f"{curr_units:,}",
                      delta=f"{units_pct_change:+.1f}% vs προηγ.")

        st.markdown("---")

        # Γεωγραφικός Χάρτης & Customer Segmentation
        col_map, col_seg = st.columns(2)

        with col_map:
            st.subheader("🗺️ Γεωγραφική Κατανομή Πωλήσεων")
            geo_df = filtered_df.groupby(['State', 'Lat', 'Lon'])['Sales'].sum().reset_index()
            fig_map = px.scatter_geo(
                geo_df, lat='Lat', lon='Lon', size='Sales', color='Sales',
                hover_name='State', size_max=40, template=plotly_template
            )
            fig_map.update_geos(projection_type="natural earth", showcountries=True)
            st.plotly_chart(fig_map, use_container_width=True)

        with col_seg:
            st.subheader("👥 Πωλήσεις ανά Τμήμα Πελατών (Segment)")
            sales_by_segment = filtered_df.groupby("Segment")["Sales"].sum().reset_index()
            fig_seg = px.bar(sales_by_segment, x="Segment", y="Sales", color="Segment", text_auto=True,
                             template=plotly_template)
            st.plotly_chart(fig_seg, use_container_width=True)

        st.markdown("---")

        # Βασικά Γραφήματα Κατηγοριών & Χρόνου
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("📊 Πωλήσεις ανά Κατηγορία")
            sales_by_cat = filtered_df.groupby("Category")["Sales"].sum().reset_index()
            fig_cat = px.bar(sales_by_cat, x="Category", y="Sales", color="Category", text_auto=True,
                             template=plotly_template)
            st.plotly_chart(fig_cat, use_container_width=True)

        with col_chart2:
            st.subheader(f"📅 Εξέλιξη Πωλήσεων ανά {time_period.split()[0]}")
            df_time = filtered_df.copy()
            if "Ημέρα" in time_period:
                df_time['Period'] = df_time['Date']
            elif "Εβδομάδα" in time_period:
                df_time['Period'] = df_time['Date'].dt.to_period('W').dt.start_time
            elif "Μήνας" in time_period:
                df_time['Period'] = df_time['Date'].dt.to_period('M').dt.start_time
            else:
                df_time['Period'] = df_time['Date'].dt.to_period('Y').dt.start_time

            sales_by_time = df_time.groupby("Period")["Sales"].sum().reset_index()
            fig_date = px.line(sales_by_time, x="Period", y="Sales", markers=True, template=plotly_template)
            st.plotly_chart(fig_date, use_container_width=True)

    # ==========================================
    # ΚΑΡΤΕΛΑ 2: AI ΑΝΑΛΥΣΕΙΣ & ΠΡΟΒΛΕΨΕΙΣ
    # ==========================================
    with tab2:
        st.markdown("### 🤖 Αυτόματα AI Insights & Smart Recommendations")
        col_ins, col_rec = st.columns(2)

        with col_ins:
            total_sales = filtered_df["Sales"].sum()
            total_profit = filtered_df["Profit"].sum()
            top_category = filtered_df.groupby("Category")["Sales"].sum().idxmax()
            top_category_sales = filtered_df.groupby("Category")["Sales"].sum().max()
            top_segment = filtered_df.groupby("Segment")["Sales"].sum().idxmax()
            profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

            st.info(
                f"• **Κορυφαία Κατηγορία:** **{top_category}** (${top_category_sales:,.0f}).\n\n"
                f"• **Κορυφαίο Τμήμα Πελατών:** **{top_segment}** οδηγεί τις πωλήσεις.\n\n"
                f"• **Περιθώριο Κέρδους:** Διαμορφώνεται στο **{profit_margin:.1f}%** (${total_profit:,.0f} καθαρό)."
            )

        with col_rec:
            top_product = filtered_df.groupby("Product")["Sales"].sum().idxmax()
            low_region = filtered_df.groupby("Region")["Sales"].sum().idxmin()

            st.success(
                f"💡 **Στρατηγική Πελατών:** Ενισχύστε τις καμπάνιες loyalty για το τμήμα **{top_segment}**.\n\n"
                f"📦 **Απόθεμα:** Διατηρήστε υψηλό stock στο **{top_product}**.\n\n"
                f"📈 **Επέκταση:** Δώστε έμφαση στην περιοχή **{low_region}** για αύξηση μεριδίου αγοράς."
            )

        st.markdown("---")

        # Μήτρα Κερδοφορίας Προϊόντων
        st.subheader("🎯 Μήτρα Κερδοφορίας Προϊόντων (Sales vs Profit Scatter Matrix)")
        prod_matrix = filtered_df.groupby(['Product', 'Category']).agg({
            'Sales': 'sum', 'Profit': 'sum', 'Units': 'sum'
        }).reset_index()

        fig_matrix = px.scatter(
            prod_matrix, x='Sales', y='Profit', color='Category', size='Units',
            hover_name='Product', template=plotly_template,
            title="Σχέση Τζίρου και Καθαρού Κέρδους ανά Προϊόν"
        )
        st.plotly_chart(fig_matrix, use_container_width=True)

        st.markdown("---")

        # Advanced AI Forecasting
        st.subheader("🔮 Advanced AI Forecasting (με Ζώνες Εμπιστοσύνης / Confidence Intervals)")

        if len(filtered_df) > 2:
            forecast_df = filtered_df.groupby("Date")["Sales"].sum().reset_index()
            forecast_df['Date_Ordinal'] = forecast_df['Date'].apply(lambda x: x.toordinal())

            X = forecast_df['Date_Ordinal']
            y = forecast_df['Sales']

            poly_fit = np.polyfit(X, y, 1)
            trend_line = np.poly1d(poly_fit)

            residuals = y - trend_line(X)
            std_err = np.std(residuals) if len(residuals) > 1 else 50.0

            last_date = forecast_df['Date'].max()
            future_dates = [last_date + pd.Timedelta(days=30 * i) for i in range(1, 6)]
            future_ordinals = [d.toordinal() for d in future_dates]
            future_preds = trend_line(future_ordinals)

            upper_bound = future_preds + (1.96 * std_err)
            lower_bound = np.maximum(0, future_preds - (1.96 * std_err))

            fig_adv = go.Figure()
            fig_adv.add_trace(
                go.Scatter(x=forecast_df['Date'], y=forecast_df['Sales'], mode='lines', name='Ιστορικές Πωλήσεις',
                           line=dict(color='blue')))
            fig_adv.add_trace(go.Scatter(x=future_dates, y=future_preds, mode='lines+markers', name='Πρόβλεψη AI',
                                         line=dict(color='orange', dash='dash')))
            fig_adv.add_trace(
                go.Scatter(x=future_dates, y=upper_bound, mode='lines', name='Best Case', line=dict(width=0),
                           showlegend=False))
            fig_adv.add_trace(
                go.Scatter(x=future_dates, y=lower_bound, mode='lines', name='95% Confidence Interval', fill='tonexty',
                           fillcolor='rgba(255, 165, 0, 0.2)', line=dict(width=0)))

            fig_adv.update_layout(title="Πρόβλεψη Τάσης Πωλήσεων με 95% Confidence Intervals", xaxis_title="Ημερομηνία",
                                  yaxis_title="Πωλήσεις ($)", template=plotly_template)
            st.plotly_chart(fig_adv, use_container_width=True)
            st.info("💡 Η σκιασμένη περιοχή απεικονίζει το διάστημα εμπιστοσύνης 95% (Best έως Worst Case σενάριο).")
        else:
            st.warning("Απαιτούνται περισσότερα δεδομένα για την πρόβλεψη στα επιλεγμένα φίλτρα ημερομηνίας.")

