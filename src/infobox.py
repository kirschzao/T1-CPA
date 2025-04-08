import os
import json
import re
import hashlib
from bs4 import BeautifulSoup

def valid_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")

def extrai_infoboxes(filepath):
    with open(filepath, "rb") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")

    infoboxes = soup.find_all("table", class_=lambda c: c and "infobox" in c)
    if not infoboxes:
        return []

    extracted = []
    for idx, infobox in enumerate(infoboxes):
        # Tentativa de extrair título (caption > th > fallback)
        caption = infobox.find("caption")
        if caption:
            title = caption.get_text(strip=True)
        else:
            th = infobox.find("th")
            title = th.get_text(strip=True) if th else f"Infobox_{idx+1}"

        data = {}
        for row in infobox.find_all("tr"):
            header = row.find("th")
            cell = row.find("td")
            if header and cell:
                key = header.get_text(strip=True)
                if cell.find("ul"):
                    values = [li.get_text(strip=True) for li in cell.find_all("li") if li.get_text(strip=True)]
                    data[key] = values
                elif cell.find("br"):
                    parts = [part.strip() for part in cell.get_text(separator="|", strip=True).split("|") if part.strip()]
                    data[key] = parts if len(parts) > 1 else parts[0]
                else:
                    data[key] = cell.get_text(strip=True)

        if data:
            extracted.append({
                "titulo": title,
                "dados": data,
                "origem_html": os.path.basename(filepath)
            })
    return extracted

def processa_infoboxes():
    pages_dir = "pages"
    output_dir = "infoboxes"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(pages_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(pages_dir, filename)
            resultados = extrai_infoboxes(filepath)

            for idx, infobox in enumerate(resultados):
                title = infobox["titulo"]
                base_name = valid_filename(title)
                origem = os.path.splitext(filename)[0]

                # Garante nome único (caso haja mais de uma infobox com mesmo título)
                hash_part = hashlib.md5(f"{title}_{idx}_{origem}".encode()).hexdigest()[:6]
                json_filename = f"{base_name}_{hash_part}.json"

                out_path = os.path.join(output_dir, json_filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(infobox, f, ensure_ascii=False, indent=2)
                print(f"Infobox salva: {out_path}".encode('utf-8', errors='replace').decode())
