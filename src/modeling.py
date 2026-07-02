import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def treinar_modelo(df):
    X = df.drop("Preco", axis=1)
    y = df["Preco"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("R²:", r2_score(y_test, y_pred))

    joblib.dump(model, "data/modelo_rf.pkl")
    print("Modelo salvo em data/modelo_rf.pkl")

    return model

if __name__ == "__main__":
    df = pd.read_csv("data/processed/imoveis_processed.csv")
    treinar_modelo(df)
