import pandas as pd

def limpar_dados(df):
    df["Preco"] = df["Preco"].str.replace("R$", "").str.replace(".", "").str.strip().astype(float)
    df["Area"] = df["Area"].str.replace("m²", "").str.strip().astype(float)
    df["Quartos"] = df["Quartos"].str.extract("(\d+)").astype(float)
    df["Banheiros"] = df["Banheiros"].str.extract("(\d+)").astype(float)
    df["Vagas"] = df["Vagas"].str.extract("(\d+)").astype(float)
    df["Preco_m2"] = df["Preco"] / df["Area"]
    return df

if __name__ == "__main__":
    df = pd.read_csv("data/raw/imoveis_raw.csv")
    df = limpar_dados(df)
    df.to_csv("data/processed/imoveis_processed.csv", index=False)
    print("Dados processados e salvos em data/processed/imoveis_processed.csv")
