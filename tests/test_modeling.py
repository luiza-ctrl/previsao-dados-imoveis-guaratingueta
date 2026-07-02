import pandas as pd
from src.modeling import treinar_modelo

def test_modelo_treina():
    df = pd.DataFrame({
        "Preco": [200000, 300000, 400000],
        "Area": [50, 70, 100],
        "Quartos": [2, 3, 4],
        "Banheiros": [1, 2, 2],
        "Vagas": [1, 2, 2],
        "Preco_m2": [4000, 4285, 4000]
    })
    model = treinar_modelo(df)
    assert model is not None
