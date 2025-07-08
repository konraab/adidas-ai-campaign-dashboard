import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 🎨 Custom Styling
st.set_page_config(page_title="Banner Performance Dashboard", layout="wide")

# 👉 Hintergrundfarbe & adidas-Stil
st.markdown("""
    <style>
    .main {
        background-color: #f0f0f0;
    }
    .block-container {
        padding: 2rem 2rem;
    }
    h1, h2, h3 {
        color: #000;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        background-color: #000;
        color: #fff;
        border-radius: 12px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Banner Performance Dashboard mit GPT Insights (Demo-Modus möglich)")

st.markdown("""
Lade deine CSV-Datei mit Kampagnen-, Produkt- und Demand-Daten hoch. Das Tool zeigt automatisch KPIs und **GPT-basierte oder simulierte Empfehlungen** je Kampagne.
""")

# 🔐 Optional: OpenAI-Key aus Streamlit Secrets
api_key = st.secrets.get("openai_api_key", None)

try:
    import openai
    if api_key:
        openai.api_key = api_key
        client_available = True
    else:
        client_available = False
except ImportError:
    client_available = False

# 📤 CSV Upload
uploaded_file = st.file_uploader("📁 CSV-Datei hochladen", type=["csv"])

# 🧠 GPT-Analyse (Dummy bei Bedarf)
def generate_campaign_insight(campaign, products, demand, start, end):
    if client_available:
        try:
            import openai
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Du bist ein datenbasierter Marketing-Analyst."},
                    {"role": "user", "content": f"""
Analysiere diese Kampagne:
Kampagne: {campaign}
Produkte: {products}
Demand: {demand}
Zeitraum: {start} bis {end}
Gib eine klare Zusammenfassung und Optimierungsempfehlung.
"""}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Fehler bei GPT: {str(e)}"

    # Dummy-Antwort
    return f"""
Die Kampagne **{campaign}** zeigt eine solide Nachfrage von **{demand:,.0f} Einheiten**. 
Die Laufzeit vom {start} bis {end} war ausreichend, jedoch könnten weitere Touchpoints mit Produkten wie *{products}* die Sichtbarkeit steigern.
👉 Empfehlung: A/B-Tests mit alternativen Creatives und stärkere Platzierung auf Conversion-starken Plattformen.
"""

# 📅 Datumsparser
def parse_date(date_str):
    return datetime.strptime(date_str + "-2025", "%d-%b-%Y")

# 🔄 App-Logik
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"Campaign", "Product", "Demand Value", "Start Date", "End Date"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Deine Datei muss folgende Spalten enthalten: {required_cols}")
    else:
        df["Start Date"] = df["Start Date"].apply(parse_date)
        df["End Date"] = df["End Date"].apply(parse_date)
        df["Demand Value"] = df["Demand Value"].astype(float)

        st.subheader("🧾 Rohdaten")
        st.dataframe(df)

        st.subheader("📈 Demand pro Kampagne")
        kampagnen_demand = df.groupby("Campaign")["Demand Value"].sum().sort_values(ascending=False)
        st.bar_chart(kampagnen_demand)

        st.subheader("🤖 GPT-Analyse je Kampagne")
        for campaign in kampagnen_demand.index:
            kampagne_data = df[df["Campaign"] == campaign]
            products = ', '.join(kampagne_data["Product"].unique())
            demand = kampagnen_demand[campaign]
            start = kampagne_data["Start Date"].min().strftime('%d.%m.%Y')
            end = kampagne_data["End Date"].max().strftime('%d.%m.%Y')

            with st.expander(f"📌 Kampagne: {campaign}"):
                insight = generate_campaign_insight(campaign, products, demand, start, end)
                st.markdown(insight)
