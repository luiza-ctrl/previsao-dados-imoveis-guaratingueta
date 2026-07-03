import json
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _normalizar_texto(texto: str) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


def _extrair_valor(texto: str, padrao: str):
    match = re.search(padrao, texto, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _parsear_texto_imovel(texto: str):
    texto = _normalizar_texto(texto)

    preco = _extrair_valor(texto, r"R\$\s*([0-9\.\,]+)")
    area = _extrair_valor(texto, r"(\d+(?:[.,]\d+)?)\s*m²")
    quartos = _extrair_valor(texto, r"(\d+)\s*quartos?")
    banheiros = _extrair_valor(texto, r"(\d+)\s*banheiros?")
    vagas = _extrair_valor(texto, r"(\d+)\s*vagas?")

    return {
        "Preco": preco,
        "Area": area,
        "Quartos": quartos,
        "Banheiros": banheiros,
        "Vagas": vagas,
    }


def _buscar_links_do_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.select("a[href]"):
        href = tag.get("href", "")
        texto = _normalizar_texto(tag.get_text(" ", strip=True))
        if not href or not texto:
            continue

        if "/imovel/" in href or "/imoveis/" in href or "/imoveis-" in href:
            links.append((href, texto))

    return links


def _parsear_json_ld(soup: BeautifulSoup):
    resultados = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            payload = json.loads(script.string or "{}")
        except Exception:
            continue

        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            items = [payload]
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            if item.get("@type") in {"Offer", "Product"}:
                nome = item.get("name", "")
                if nome:
                    resultados.append(_parsear_texto_imovel(nome))

            elif item.get("@type") == "ItemList":
                for element in item.get("itemListElement", []):
                    if isinstance(element, dict):
                        nome = element.get("name", "")
                        if nome:
                            resultados.append(_parsear_texto_imovel(nome))

    return resultados


def _fetch_html(url: str, timeout: int = 25) -> str:
    session = requests.Session()
    session.headers.update(HEADERS)

    for tentativa in range(3):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            if tentativa == 2:
                raise RuntimeError(f"Falha ao acessar {url}: {exc}") from exc
            time.sleep(1)


def _coletar_provider(url: str):
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    links = _buscar_links_do_html(html)
    dados = []

    for _, texto in links:
        parsed = _parsear_texto_imovel(texto)
        if parsed["Preco"] or parsed["Area"]:
            dados.append(parsed)

    if not dados:
        for parsed in _parsear_json_ld(soup):
            if parsed["Preco"] or parsed["Area"]:
                dados.append(parsed)

    return dados


def coletar_imoveis(paginas=5):
    providers = [
        {
            "nome": "vivareal",
            "url_template": "https://www.vivareal.com.br/venda/sp/guaratingueta/?pagina={}",
        },
        {
            "nome": "zapimoveis",
            "url_template": "https://www.zapimoveis.com.br/venda/sp/guaratingueta/?pagina={}",
        },
        {
            "nome": "olx",
            "url_template": "https://www.olx.com.br/imoveis/sp-guaratingueta-e-regiao/venda/?o={}",
        },
    ]

    resultados = []
    vistos = set()

    for provider in providers:
        nome = provider["nome"]
        template = provider["url_template"]

        print(f"Buscando em {nome}...")

        for page in range(1, paginas + 1):
            url = template.format(page)
            try:
                dados = _coletar_provider(url)
            except Exception as exc:
                print(f"  Página {page}: erro em {nome} -> {exc}")
                continue

            print(f"  Página {page}: {len(dados)} itens encontrados em {nome}")

            for item in dados:
                chave = (
                    item["Preco"],
                    item["Area"],
                    item["Quartos"],
                    item["Banheiros"],
                    item["Vagas"],
                )
                if chave in vistos:
                    continue
                vistos.add(chave)
                resultados.append(item)

    return pd.DataFrame(
        resultados,
        columns=["Preco", "Area", "Quartos", "Banheiros", "Vagas"],
    )


if __name__ == "__main__":
    df = coletar_imoveis(paginas=5)

    output_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "imoveis_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        print("Atenção: nenhum imóvel foi coletado.")
    else:
        df.to_csv(output_path, index=False)
        print(f"Dados coletados e salvos em {output_path}")