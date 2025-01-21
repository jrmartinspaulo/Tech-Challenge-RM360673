from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Dicionário com as URLs das seções do site
SECTIONS_URLS = {
    "producao": "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02",
    "processamento": "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03",
    "comercializacao": "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04",
    "importacao": "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05",
    "exportacao": "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06",
}

def fetch_data_from_url(url):
    """
    Realiza uma requisição para a URL fornecida e retorna os dados extraídos.
    Caso haja uma tabela na página, os dados são organizados em formato JSON.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta exceções para erros HTTP
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Busca pela primeira tabela na página
        table = soup.find("table")
        if table:
            # Extração das linhas e células da tabela
            extracted_data = []
            for row in table.find_all("tr"):
                cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
                extracted_data.append(cells)
            return {"status": "success", "data": extracted_data}
        
        return {"status": "success", "message": "Nenhuma tabela encontrada na página."}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Erro na requisição: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro inesperado: {str(e)}"}

@app.route("/", methods=["GET"])
def index():
    """
    Endpoint raiz para exibir informações básicas sobre a API e seus endpoints disponíveis.
    """
    return jsonify({
        "message": "Bem-vindo à API de dados de vitivinicultura!",
        "instructions": "Use os endpoints abaixo para acessar os dados específicos:",
        "endpoints": list(SECTIONS_URLS.keys())
    })

@app.route("/<section>", methods=["GET"])
def get_section(section):
    """
    Endpoint para obter os dados de uma das seções disponíveis.
    """
    # Verifica se a seção solicitada é válida
    if section not in SECTIONS_URLS:
        return jsonify({
            "error": "Seção inválida. Consulte os endpoints disponíveis no endpoint raiz (/)."
        }), 400
    
    # Busca os dados da URL correspondente
    url = SECTIONS_URLS[section]
    data = fetch_data_from_url(url)
    return jsonify({
        "section": section,
        "data": data
    })

@app.route("/favicon.ico")
def ignore_favicon():
    """
    Ignora solicitações ao favicon para evitar erros no log.
    """
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
