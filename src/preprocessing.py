from pathlib import Path
import pandas as pd

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Preço: remover símbolo, espaços, pontos de milhar e trocar vírgula por ponto
    if "Preco" in df.columns:
        s = df["Preco"].fillna("").astype(str)
        s = (
            s.str.replace("R$", "", regex=False)
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)  # remove separador de milhares
             .str.replace(",", ".", regex=False)  # normaliza decimal
             .str.strip()
        )
        df["Preco"] = pd.to_numeric(s, errors="coerce")

    # Área: remover 'm²', espaços, pontos de milhar e normalizar vírgula
    if "Area" in df.columns:
        s = df["Area"].fillna("").astype(str)
        s = (
            s.str.replace("m²", "", regex=False)
             .str.replace(" ", "", regex=False)
             .str.replace(".", "", regex=False)
             .str.replace(",", ".", regex=False)
             .str.strip()
        )
        df["Area"] = pd.to_numeric(s, errors="coerce")

    # Quartos / Banheiros / Vagas: extrair dígitos com segurança
    for col in ("Quartos", "Banheiros", "Vagas"):
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].fillna("").astype(str).str.extract(r"(\d+)", expand=False),
                errors="coerce",
            )

    # Preço por m2 — evita divisão por zero e trata valores ausentes
    if "Preco" in df.columns and "Area" in df.columns:
        df["Preco_m2"] = df["Preco"] / df["Area"]
        df.loc[(df["Area"].isna()) | (df["Area"] == 0), "Preco_m2"] = pd.NA
    else:
        df["Preco_m2"] = pd.NA

    return df


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    raw_path = repo_root / "data" / "raw" / "imoveis_raw.csv"
    processed_dir = repo_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_file = processed_dir / "imoveis_processed.csv"

    if not raw_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {raw_path}")

    df = pd.read_csv(raw_path)
    df = limpar_dados(df)
    df.to_csv(out_file, index=False)
    print(f"Dados processados e salvos em {out_file}")