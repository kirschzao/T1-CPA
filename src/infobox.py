import os
import json
import re
from bs4 import BeautifulSoup

def extrai_infobox(filepath):
    # Abre o arquivo HTML, procura a infobox e extrai:
    # Título e Pares chave-valor 
    # Retorna um dicionário com o título e os dados extraídos ou None se a infobox não for encontrada.


    with open(filepath, "rb") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    
    # Procura por uma table q tem "infobox" ou none
    infobox = soup.find("table", class_=lambda c: c and "infobox" in c)
    if not infobox:
        return None 
    
    # Tenta extrair o título da infobox 
    # primeiro pelo caption
    # depois pelo primeiro th
    caption = infobox.find("caption")
    if caption:
        title = caption.get_text(strip=True)
    else:
        first_th = infobox.find("th")
        title = first_th.get_text(strip=True) if first_th else "Infobox"
    
    data = {}
    # Itera por todas as linhas da tabela
    for row in infobox.find_all("tr"):
        header = row.find("th")
        cell = row.find("td")
        if header and cell:
            key = header.get_text(strip=True)
            # Se existir uma lista (<ul>), extrai cada item
            if cell.find("ul"):
                values = [li.get_text(strip=True) for li in cell.find_all("li") if li.get_text(strip=True)]
                data[key] = values
            else:
                # Se houver quebras de linha (<br>), usamos um separador para criar lista
                if cell.find("br"):
                    text = cell.get_text(separator="|", strip=True)
                    parts = [part.strip() for part in text.split("|") if part.strip()]
                    data[key] = parts if len(parts) > 1 else parts[0]
                else:
                    data[key] = cell.get_text(strip=True)
    
    return {"titulo": title, "dados": data}



def processa_infoboxes():
    #Percorre todos os arquivos HTML da pasta 'pages', extrai as infoboxes (quando existirem)
    #e salva os dados extraídos em arquivos JSON. O JSON será criado apenas se a infobox
    #possuir pelo menos um par chave:valor.

    pages_dir="pages"
    output_dir="infoboxes"
    
    for filename in os.listdir(pages_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(pages_dir, filename)
            result = extrai_infobox(filepath)

            # Verifica se a infobox foi encontrada e se possui pelo menos um atributo
            if result is not None and result.get("dados"):
                json_filename = re.sub(r'[\\/*?:"<>|]', "", result["titulo"]).replace(" ", "_") + ".json"
                out_path = os.path.join(output_dir, json_filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"Infobox salva: {out_path}")
