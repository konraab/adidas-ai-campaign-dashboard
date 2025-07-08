import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
from datetime import datetime

# OpenAI API-Key aus Streamlit Secrets laden
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="Banner Performance AI Dashboard", layout="wide")
st.title("📊 Banner Performance Dashboard mit GPT Insights")

st.markdown("""
Lade deine CSV-Datei mit Kampagnen-, Produkt- und Demand-Daten hoch. Das Tool zeigt automatisch KPIs und AI-generierte Insights je Kampagne.
""")

uploaded_file = st.file_uploader("📁 CSV-Datei hochladen", type=["csv"])

def parse_date(date_str):
    # Datum im Format '6-Mar' zu datetime-Objekt (aktuelles Jahr)
    return datetime.strptime(date_str + "-2025", "%d-%b-%Y")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Prüfen ob alle nötigen Spalten da sind
    required_cols = {"Campaign", "Product", "Demand Value", "Start Date", "End Date"}
    if not required_cols.issubset(df.columns):
        st.error(f"Deine Datei muss folgende Spalten enthalten: {required_cols}")
    else:
        # Datumsspalten umwandeln
        df["Start Date"] = df["Start Date"].apply(parse_date)
        df["End Date"] = df["End Date"].apply(parse_date)

        # Demand Value als float
        df["Demand Value"] = df["Demand Value"].astype(float)

        # Rohdaten anzeigen
        st.subheader("🧾 Rohdaten")
        st.dataframe(df)

        # Kampagnen-Demand je Kampagne summieren
        st.subheader("📈 Kampagnen Demand Vergleich")
        kampagnen_demand = df.groupby("Campaign")["Demand Value"].sum().sort_values(ascending=False)
        st.bar_chart(kampagnen_demand)

        # GPT Insights generieren für jede Kampagne
        st.subheader("🤖 GPT Insights je Kampagne")

        for campaign in kampagnen_demand.index:
            kampagne_data = df[df["Campaign"] == campaign]

            prompt = f"""
Du bist ein Marketing-Analyst. Analysiere folgende Kampagnendaten:
Kampagne: {campaign}
Produkte: {', '.join(kampagne_data['Product'].unique())}
Gesamte Nachfrage (Demand Value): {kampagnen_demand[campaign]}
Laufzeit: {kampagne_data['Start Date'].min().strftime('%d.%m.%Y')} bis {kampagne_data['End Date'].max().strftime('%d.%m.%Y')}

Gib eine kurze, verständliche Zusammenfassung und eine Empfehlung zur Optimierung der Kampagne.
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7,
            )

            insight = response.choices[0].message.content.strip()

            st.markdown(f"### Kampagne: {campaign}")
            st.write(insight)
