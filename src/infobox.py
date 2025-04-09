import os
import json
import re
import hashlib
from bs4 import BeautifulSoup

def valid_filename(name):
    """Remove caracteres inválidos e substitui espaços por underscores."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")

def safe_print(text):
    print(text.encode("ascii", "ignore").decode())

def extrai_infoboxes(filepath):
    """Extrai todas as infoboxes de um arquivo HTML."""
    with open(filepath, "rb") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")

    # Pega qualquer <table> com 'infobox' na classe
    infoboxes = soup.find_all("table", class_=lambda c: c and "infobox" in c)
    if not infoboxes:
        return []

    extraidas = []
    for idx, infobox in enumerate(infoboxes):
        # Tenta obter o título da infobox
        caption = infobox.find("caption")
        if caption:
            title = caption.get_text(strip=True)
        else:
            th = infobox.find("th")
            title = th.get_text(strip=True) if th else f"Infobox_{idx+1}"

        dados = {}
        for row in infobox.find_all("tr"):
            header = row.find("th")
            cell = row.find("td")
            if header and cell:
                chave = header.get_text(strip=True)
                if cell.find("ul"):
                    dados[chave] = [li.get_text(strip=True) for li in cell.find_all("li")]
                elif cell.find("br"):
                    partes = [part.strip() for part in cell.get_text(separator="|", strip=True).split("|") if part.strip()]
                    dados[chave] = partes if len(partes) > 1 else partes[0]
                else:
                    dados[chave] = cell.get_text(strip=True)

        if dados:
            extraidas.append({
                "titulo": title,
                "dados": dados,
                "origem_html": os.path.basename(filepath)
            })

    return extraidas

def processa_infoboxes():
    pages_dir = "pages"
    output_dir = "infoboxes"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(pages_dir):
        if filename.lower().endswith(".html"):
            caminho_html = os.path.join(pages_dir, filename)
            infoboxes = extrai_infoboxes(caminho_html)

            for idx, infobox in enumerate(infoboxes):
                titulo = infobox["titulo"]
                nome_base = valid_filename(titulo)
                origem = os.path.splitext(filename)[0]

                # Nome único com hash curto
                hash_id = hashlib.md5(f"{titulo}_{idx}_{origem}".encode()).hexdigest()[:6]
                nome_json = f"{nome_base}_{hash_id}.json"

                caminho_saida = os.path.join(output_dir, nome_json)
                with open(caminho_saida, "w", encoding="utf-8") as f:
                    json.dump(infobox, f, ensure_ascii=False, indent=2)
                safe_print(f"Infobox salva: {caminho_saida}")







