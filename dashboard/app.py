import streamlit as st
import pandas as pd
import joblib

st.title("Previsão de Preços de Imóveis - Guaratinguetá")

# Carregar modelo treinado
model = joblib.load("data/modelo_rf.pkl")

area = st.number_input("Área (m²)", min_value=20, max_value=500)
quartos = st.number_input("Quartos", min_value=1, max_value=10)
banheiros = st.number_input("Banheiros", min_value=1, max_value=10)
vagas = st.number_input("Vagas", min_value=0, max_value=5)

if st.button("Prever preço"):
    entrada = pd.DataFrame([[area, quartos, banheiros, vagas, area/quartos]],
                           columns=["Area", "Quartos", "Banheiros", "Vagas", "Preco_m2"])
    preco = model.predict(entrada)[0]
    st.success(f"Preço estimado: R$ {preco:,.2f}")
