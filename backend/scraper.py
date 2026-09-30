import re
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from database import obter_conexao

# URL de destino
URL_NOTICIAS = "https://www4.unievangelica.edu.br/noticia"

# Data limite para filtro: 01 de Agosto de 2026
DATA_CORTE = datetime(2026, 8, 1)

# Listas de palavras-chave para filtro
KEYWORDS_TECH = [
    'tecnologia', 'programação', 'desenvolvimento', 'software', 'ti', 
    'inteligência artificial', 'ia', 'python', 'javascript', 'algoritmo',
    'computação', 'hackathon', 'maratona', 'dados', 'cybersecurity', 'sistema',
    'engenharia de software', 'sistemas de informação', 'ciência da computação',
    'análise e desenvolvimento', 'inovação', 'ciência'
]

KEYWORDS_EVENTOS = [
    'evento', 'workshop', 'palestra', 'semana acadêmica', 'webinar',
    'simpósio', 'conferência', 'inscrições abertas', 'minicurso', 'meetup',
    'sinacen', 'semana', 'jornada', 'congresso', 'começa hoje', 'início'
]

KEYWORDS_IGNORAR = [
    'fale com', 'reitor', 'ouvidoria', 'trabalhe conosco', 'portal do aluno',
    'área do aluno', 'seja bem-vindo', 'politica de privacidade', 'como ingressar',
    'fale conosco', 'agende sua visita', 'inscreva-se', 'editais', 'graduação', 'pós-graduação'
]

def contem_palavra_chave(texto, keywords):
    """Verifica se alguma palavra-chave está presente no texto tratando limites de palavras."""
    for kw in keywords:
        pattern = rf'\b{re.escape(kw)}\b'
        if re.search(pattern, texto, re.IGNORECASE):
            return True
    return False

def classificar_noticia(titulo):
    """Analisa o título e classifica por relevância e categoria."""
    titulo_lc = titulo.lower()
    
    eh_tech = contem_palavra_chave(titulo_lc, KEYWORDS_TECH)
    eh_evento = contem_palavra_chave(titulo_lc, KEYWORDS_EVENTOS)
    
    if eh_tech and eh_evento:
        return 'Evento de Software', True
    elif eh_tech:
        return 'Tecnologia', True
    elif eh_evento:
        return 'Evento', False
    
    return 'Geral', False

def parse_data(data_str):
    """Converte 'dd/mm/aa' ou 'dd/mm/yyyy' para objeto datetime."""
    try:
        data_str = data_str.strip()
        if len(data_str.split('/')[-1]) == 2:
            return datetime.strptime(data_str, "%d/%m/%y")
        return datetime.strptime(data_str, "%d/%m/%Y")
    except (ValueError, AttributeError):
        return None

def monitorar_homepage():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    conn = None
    cursor = None

    try:
        response = requests.get(URL_NOTICIAS, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Limpeza de elementos de navegação/ruído
        for lixo in soup.select('nav, footer, header, aside, .menu, .sidebar, .footer, .btn, .botao, .atendimento'):
            lixo.decompose()

        # 2. Seleção de artigos/cards
        artigos = soup.select('article, div.noticia, .post-item, .card, a[href*="noticia"]')

        conn = obter_conexao()
        cursor = conn.cursor()
        noticias_processadas = 0
        links_processados = set()

        # 3. Filtragem, limite de 20 e gravação
        for item in artigos:
            # Trava para capturar no máximo 20 notícias por execução
            if noticias_processadas >= 20:
                break

            link_tag = item if item.name == 'a' else item.find('a')
            if not link_tag or not link_tag.get('href'):
                continue

            # Extração da data via tag <span>
            span_data = item.find('span')
            data_noticia = parse_data(span_data.text) if span_data else None

            # Filtro de data: se houver data e for anterior a 01/08/2026, descarta
            if data_noticia and data_noticia < DATA_CORTE:
                continue

            # Destrói a tag de data do elemento HTML para impedir que ela fique colada no título
            if span_data:
                span_data.decompose()

            # Extração limpa do título utilizando separador de espaço
            titulo_raw = link_tag.get_text(separator=' ', strip=True)

            # Insere espaço entre letras minúsculas e maiúsculas coladas (ex: AnápolisUniEVANGÉLICA)
            titulo_tratado = re.sub(r'([a-zà-ú])([A-ZÀ-Ú])', r'\1 \2', titulo_raw)

            # 2. Correção específica para a marca (Junta 'Uni EVANGÉLICA' ou 'Uni EVANGELICA' novamente)
            titulo_tratado = re.sub(r'\bUni\s+EVANGÉLICA\b', 'UniEVANGÉLICA', titulo_tratado, flags=re.IGNORECASE)
            titulo_tratado = re.sub(r'\bUni\s+EVANGELICA\b', 'UniEVANGÉLICA', titulo_tratado, flags=re.IGNORECASE)
            # Insere espaço entre texto e números/datas coladas
            # 3. Insere espaço entre texto e números/datas
            titulo = re.sub(r'([a-zA-ZáàâãéèêíóôõúçÁÀÂÃÉÈÊÍÓÔÕÚÇ])(\d+º?)', r'\1 \2', titulo_tratado)
            titulo = " ".join(titulo.split())  # Normaliza múltiplos espaços

            link_bruto = link_tag['href'].strip()

            if not titulo or len(titulo) < 15:
                continue

            titulo_lc = titulo.lower()
            if any(termo in titulo_lc for termo in KEYWORDS_IGNORAR):
                continue

            link = urljoin(URL_NOTICIAS, link_bruto)

            if link in links_processados:
                continue
            links_processados.add(link)

            categoria, eh_relevante = classificar_noticia(titulo)
            data_sql = data_noticia.strftime("%Y-%m-%d") if data_noticia else None

            # SQL utilizando ON DUPLICATE KEY UPDATE para atualizar dados sem duplicar
            sql = """
                INSERT INTO noticias (titulo, link, categoria, eh_relevante, data_publicacao) 
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    titulo = VALUES(titulo),
                    categoria = VALUES(categoria),
                    eh_relevante = VALUES(eh_relevante),
                    data_publicacao = COALESCE(VALUES(data_publicacao), data_publicacao)
            """
            cursor.execute(sql, (titulo, link, categoria, eh_relevante, data_sql))
            noticias_processadas += 1

        conn.commit()
        print(f"[FoxxPI Scraper] Processamento concluído. Itens verificados/atualizados: {noticias_processadas}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[FoxxPI Scraper] Erro durante a varredura: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    monitorar_homepage()