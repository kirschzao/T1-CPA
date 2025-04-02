from src.scraping import crawler
from src.infobox import processa_infoboxes

def main():
    print("Iniciando o crawler")
    crawler()
    print("Crawler finalizado.")
    print("Iniciando a scrap das infoboxes")
    processa_infoboxes()
    print("Projeto concluído.")

if __name__ == "__main__":
    main()
