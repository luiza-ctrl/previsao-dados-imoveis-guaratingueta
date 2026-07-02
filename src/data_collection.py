import requests
from bs4 import BeautifulSoup
import pandas as pd

def coletar_imoveis(base_url, paginas=5):
    imoveis = []
    for page in range(1, paginas+1):
        url = base_url.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for card in soup.find_all("div", class_="property-card__content"):
            try:
                preco = card.find("div", class_="property-card__price").text.strip()
                area = card.find("span", class_="property-card__detail-area").text.strip()
                quartos = card.find("li", class_="property-card__detail-room").text.strip()
                banheiros = card.find("li", class_="property-card__detail-bathroom").text.strip()
                vagas = card.find("li", class_="property-card__detail-garage").text.strip()
                imoveis.append([preco, area, quartos, banheiros, vagas])
            except:
                continue

    df = pd.DataFrame(imoveis, columns=["Preco", "Area", "Quartos", "Banheiros", "Vagas"])
    return df

if __name__ == "__main__":
    base_url = "https://www.vivareal.com.br/venda/sp/guaratingueta/?pagina={}"
    df = coletar_imoveis(base_url)
    df.to_csv("data/raw/imoveis_raw.csv", index=False)
    print("Dados coletados e salvos em data/raw/imoveis_raw.csv")
