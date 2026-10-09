import re
import threading
import os

import requests
from bs4 import BeautifulSoup

LINKS = []

#https://mangalivre.blog/manga/isekai-meikyuu-de-harem-wo/

def pedir_manga():
    while True:
        manga_escolhido = input("Insira o link do manga escolhido para download dos capítulos: ")
        resposta = requisicao(manga_escolhido)
        if not resposta:
            print("Não foi possível acessar esse link. Tente novamente.")
            continue

        soup = parsing(resposta)
        if not soup:
                ("Não foi possível interpretar a página!")
                continue
        links = encontrar_links(soup)
        if not links:
            print("Nenhum capítulo encontrado, valide o link inserido!")

        print(f"\nCapítulos encontrados: {len(links)}")
        return links


def encontrar_capitulo(lista_de_capitulos, numero):
    for link in lista_de_capitulos:
        if f"capitulo-{numero}/" in link:
            return link

    return None


def menu(lista_de_capitulos):
    while True:
        print("\n--- MENU ---")
        print("1 - Baixar todos")
        print("2 - Baixar capítulo específico")
        print("0 - Sair")

        opcao = input("Escolha: ")

        if opcao == "1":
            return lista_de_capitulos

        elif opcao == "2":
            numero = input("Número do capítulo: ")

            link_encontrado = encontrar_capitulo(
                lista_de_capitulos,
                numero
            )

            if link_encontrado:
                return [link_encontrado]

            else:
                print("Capítulo não encontrado")

        elif opcao == "0":
            return None

        else:
            print("Opção inválida")


def requisicao(url):
    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            return resposta.text
        else:
            print("Erro ao fazer requisição 1")

    except Exception as erro:
        print("Erro ao fazer requisição")
        print(erro)


def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html,"html.parser") 
        return soup
    except Exception as error:
        print("Erro ao fazer Parsing")
        print(error)


def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="chapters-grid" )
        cards = cards_pai.find_all("article", class_="chapter-grid-item") 
    except Exception as error:
        print("Erro ao encontrar links")
        print(error)
        return None
        
    links = []
    for card in cards:
        try:
            link = card.find("a")["href"]
            links.append(link)
        except:
            pass
    return links


def encontrar_img(soup):
    imagens = soup.find_all("img",class_="chapter-image")

    link_imagens = []

    for imagem in imagens:
        link = imagem.get("src")
        if link:
            link_imagens.append(link)

    return link_imagens


def descobrir_imagem():
    while True:
        try:
            link_capitulo = LINKS.pop(0)
        except:
            return

        resposta_capitulo = requisicao(link_capitulo) 

        if resposta_capitulo:
            soup_capitulo = parsing(resposta_capitulo)

            if soup_capitulo:
                imagens = encontrar_img(soup_capitulo)
                if imagens:
                    nome_pasta = link_capitulo.rstrip("/").split("/")[-1]

                    os.makedirs(nome_pasta, exist_ok=True) 

                    print(f"\nBaixando {nome_pasta}...")

                    for index, imagem in enumerate(imagens):
                        baixar_imagem(imagem, nome_pasta, index + 1)


def baixar_imagem(url, pasta, numero):
    try:
        resposta = requests.get(url, timeout=10)

        if resposta.status_code == 200:
            nome_arquivo = f"pagina_{numero}.webp"
            caminho = os.path.join(pasta, nome_arquivo)

            with open(caminho, "wb") as arquivo:
                arquivo.write(resposta.content)

            print("Salvou:", caminho)

    except Exception as erro:
        print("Erro ao baixar imagem")
        print(erro)


if __name__ == "__main__":
    LINKS_ENCONTRADOS = pedir_manga()

    LINKS = menu(LINKS_ENCONTRADOS)

    if LINKS:
        THREADS = []

        quantidade_threads = min(14, len(LINKS))

        for _ in range(quantidade_threads):
            t = threading.Thread(target=descobrir_imagem)
            THREADS.append(t)

        for t in THREADS:
            t.start()

        for t in THREADS:
            t.join()

        print("\nDownload concluído.")