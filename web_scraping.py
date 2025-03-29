import requests
from bs4 import BeautifulSoup
import os
import zipfile

# URL da página da ANS
URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
response = requests.get(URL)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = []
    
    # Encontra todos os links na página
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf') and ('anexo-i' in href.lower() or 'anexo-ii' in href.lower()):
            pdf_links.append(href if href.startswith('http') else f'https://www.gov.br{href}')

    if not pdf_links:
        print("Nenhum PDF encontrado.")
    else:
        # Criar pasta para armazenar os PDFs
        os.makedirs("pdfs", exist_ok=True)
        
        for pdf_url in pdf_links:
            pdf_name = pdf_url.split("/")[-1]
            pdf_path = os.path.join("pdfs", pdf_name)
            
            print(f"Baixando: {pdf_name}")
            pdf_response = requests.get(pdf_url)
            with open(pdf_path, "wb") as f:
                f.write(pdf_response.content)
        
        # Compactação dos PDFs
        zip_filename = "anexos.zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for file in os.listdir("pdfs"):
                zipf.write(os.path.join("pdfs", file), arcname=file)
        
        print(f"Arquivos compactados em {zip_filename}")
else:
    print("Falha ao acessar a página.")
