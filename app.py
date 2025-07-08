import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from openai import OpenAI
import os

# Styling (Adidas-like + grauer Hintergrund)
st.set_page_config(page_title="Adidas Banner Dashboard", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #f2f2f2;
        }
        .block-container {
            padding-top: 2rem;
        }
        h1 {
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Adidas Campaign Dashboard mit GPT Insights")

st.markdown("""
Lade deine CSV-Datei mit Kampagnen-, Produkt- und Demand-Daten hoch. Die App zeigt KPIs und GPT-gestützte Analysen – gesteuert per Button.
""")

uploaded_file = st.file_uploader("📁 CSV-Datei hochladen", type=["csv"])

def parse_date(date_str):
    return datetime.strptime(date_str + "-2025", "%d-%b-%Y")

# OpenAI Client Setup
try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except KeyError:
    st.error("❌ OpenAI API-Key fehlt in den Secrets. Lege ihn unter `.streamlit/secrets.toml` an.")
    st.stop()

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"Campaign", "Product", "Demand Value", "Start Date", "End Date"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Die Datei muss folgende Spalten enthalten: {required_cols}")
        st.stop()

    df["Start Date"] = df["Start Date"].apply(parse_date)
    df["End Date"] = df["End Date"].apply(parse_date)
    df["Demand Value"] = df["Demand Value"].astype(float)

    st.subheader("🧾 Rohdaten")
    st.dataframe(df)

    st.subheader("📈 Kampagnen Demand Vergleich")
    kampagnen_demand = df.groupby("Campaign")["Demand Value"].sum().sort_values(ascending=False)
    st.bar_chart(kampagnen_demand)

    st.subheader("🤖 GPT Insights – je Kampagne abrufbar")

    for campaign in kampagnen_demand.index:
        with st.expander(f"🔍 Kampagne: {campaign}"):
            kampagne_data = df[df["Campaign"] == campaign]
            if st.button(f"GPT Insight generieren für '{campaign}'"):
                with st.spinner("GPT analysiert die Kampagne..."):
                    prompt = f"""
                    Du bist ein Marketing-Analyst. Analysiere folgende Kampagnendaten:
                    Kampagne: {campaign}
                    Produkte: {', '.join(kampagne_data['Product'].unique())}
                    Gesamte Nachfrage (Demand Value): {kampagnen_demand[campaign]}
                    Laufzeit: {kampagne_data['Start Date'].min().strftime('%d.%m.%Y')} bis {kampagne_data['End Date'].max().strftime('%d.%m.%Y')}

                    Gib eine klare, kurze Zusammenfassung + Optimierungsempfehlung für das Marketing-Team.
                    """

                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Du bist ein Marketing-Analyst."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=300,
                            temperature=0.7,
                        )
                        st.success("✅ Insight generiert:")
                        st.write(response.choices[0].message.content.strip())
                    except Exception as e:
                        st.error(f"Fehler bei der Anfrage an GPT: {e}")
