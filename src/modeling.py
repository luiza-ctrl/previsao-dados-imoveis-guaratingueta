from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


def treinar_modelo(df: pd.DataFrame):
    if df.empty:
        raise ValueError(
            "DataFrame vazio. Verifique se data/processed/imoveis_processed.csv contém dados."
        )

    if "Preco" not in df.columns:
        raise ValueError("Coluna 'Preco' não encontrada no DataFrame.")

    df = df.copy()
    df["Preco"] = pd.to_numeric(df["Preco"], errors="coerce")

    feature_cols = [col for col in df.columns if col != "Preco"]
    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Preco"]).copy()

    if df.empty:
        raise ValueError("Não há linhas válidas com preço para treinar o modelo.")

    X = df.drop(columns=["Preco"])
    y = df["Preco"]

    if X.empty:
        raise ValueError("Não há colunas preditoras além de 'Preco'.")

    X = X.fillna(X.median())

    if len(y.dropna()) < 2:
        raise ValueError(
            "Quantidade insuficiente de amostras válidas para treino. "
            "Verifique se o arquivo processado contém linhas de dados."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("R²:", r2_score(y_test, y_pred))

    model_path = Path(__file__).resolve().parent.parent / "data" / "modelo_rf.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Modelo salvo em {model_path}")

    return model


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    input_path = repo_root / "data" / "processed" / "imoveis_processed.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

    df = pd.read_csv(input_path)
    treinar_modelo(df)