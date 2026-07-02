import pandas as pd
import matplotlib.pyplot as plt

def grafico_precos(df):
    plt.figure(figsize=(8,6))
    plt.scatter(df["Area"], df["Preco"], alpha=0.7)
    plt.xlabel("Área (m²)")
    plt.ylabel("Preço (R$)")
    plt.title("Preço vs Área dos Imóveis")
    plt.show()

if __name__ == "__main__":
    df = pd.read_csv("data/processed/imoveis_processed.csv")
    grafico_precos(df)
