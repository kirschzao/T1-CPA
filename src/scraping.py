import requests
from bs4 import BeautifulSoup
import os
import time
import re


link = "https://pt.wikipedia.org"
START_URL = link

def valida_link(link):
  #Verifica se o link inicia com '/wiki/'
  if link is None:
    return False
    
  if not link.startswith("/wiki/"):
    return False
    
  # Após '/wiki/', links com ':' indicam páginas internas que não são verbetes
  pages = link[len("/wiki/"):]
  if ":" in pages:
    return False
  return True

def valid_filename(title):
  filename = re.sub(r'[\\/*?:"<>|]', "", title)
  filename = filename.replace(" ", "_")
  return filename

def crawler():

  #ara armazenar URLs já visitadas
  visited = set()  
  #Fila de URLs a visitar
  queue = [START_URL]  

  while queue and len(visited) <= 5000:
    url = queue.pop(0)
    if url in visited:
      continue

    try:
      response = requests.get(url)
    except Exception as e:
      print(f"Erro ao acessar {url}: {e}")
      continue

    if response.status_code != 200:
      print(f"Falha ao acessar {url}: status code {response.status_code}")
      continue

    soup = BeautifulSoup(response.content, "html.parser")

    # Extrai o título da página
    title_tag = soup.find("title")
    if title_tag:
      # Muitas vezes o título vem no formato "Título - Wikipédia, a enciclopédia livre"
      title = title_tag.get_text().split(" - ")[0]
    else:
      title = "sem_titulo"

    # Cria um nome de arquivo seguro a partir do título
    filename = valid_filename(title) + ".html"
    
    # Define o caminho para salvar os arquivos na pasta "pages"
    filepath = os.path.join("pages", filename)
    
    with open(filepath, "wb") as f:
      f.write(response.content)
    print(f"Salvei: {filepath}")

    # Salva a URL visitada
    visited.add(url)

    # Extrai e filtra os links da página
    for a_tag in soup.find_all("a"):
      linked = a_tag.get("href")
      if valida_link(linked):
        full_url = link + linked
        if full_url not in visited and full_url not in queue:
          queue.append(full_url)

    # Delay para evitar sobrecarregar o servidor
    time.sleep(0.5)

  print(f"Crawling finalizado. Páginas visitadas: {len(visited)}")


