import os
import requests
import zipfile
import tabula
import pandas as pd
from bs4 import BeautifulSoup

def get_pdf_links(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = []
    for link in soup.find_all('a', href=True):
        if "Anexo" in link.text and link['href'].endswith(".pdf"):
            pdf_links.append(link['href'])
    return pdf_links

def download_pdfs(pdf_links, download_dir):
    os.makedirs(download_dir, exist_ok=True)
    downloaded_files = []
    for pdf_url in pdf_links:
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join(download_dir, pdf_name)
        try:
            pdf_response = requests.get(pdf_url, timeout=10)
            pdf_response.raise_for_status()
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_response.content)
            downloaded_files.append(pdf_path)
            print(f"Baixado: {pdf_name}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar {pdf_name}: {e}")
    return downloaded_files

def create_zip(files, zip_path):
    if not files:
        print("Nenhum arquivo para compactar.")
        return
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    print(f"Arquivo ZIP criado em: {zip_path}")

def extract_table_from_pdf(pdf_path):
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    if tables:
        return tables[0]
    return None

def save_to_csv_and_zip(dataframe, csv_path, zip_path):
    dataframe.to_csv(csv_path, index=False)
    print(f"Arquivo CSV criado em: {csv_path}")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv_path, os.path.basename(csv_path))
    print(f"Arquivo ZIP criado com o CSV em: {zip_path}")

def replace_abbreviations(df):
    abbreviations = {
        'OD': 'Olho Direito',
        'AMB': 'Ambulatório'
    }
    df.replace(abbreviations, inplace=True)
    return df

def main():
    url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
    download_dir = "downloads"
    zip_path = os.path.join(download_dir, "anexos.zip")
    
    print("Obtendo links dos PDFs...")
    pdf_links = get_pdf_links(url)
    if not pdf_links:
        print("Nenhum link de PDF encontrado.")
        return
    
    print("Baixando PDFs...")
    downloaded_files = download_pdfs(pdf_links, download_dir)
    
    pdf_path = downloaded_files[0]
    print("Extraindo dados da tabela do PDF...")
    table = extract_table_from_pdf(pdf_path)
    
    if table is None:
        print("Nenhuma tabela encontrada no PDF.")
        return
    
    print("Substituindo abreviações e salvando em CSV...")
    df = pd.DataFrame(table)
    df = replace_abbreviations(df)
    csv_path = os.path.join(download_dir, "rol_de_procedimentos.csv")
    save_to_csv_and_zip(df, csv_path, os.path.join(download_dir, "Teste_Wellyson.zip"))

    print("Criando arquivo ZIP com os PDFs...")
    create_zip(downloaded_files, zip_path)
    
if __name__ == "__main__":
    main()
