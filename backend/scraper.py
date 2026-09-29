import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from database import obter_conexao

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
    
    # Evento focado em TI ou Ciência/Inovação vai direto para Eventos Tech
    if eh_tech and eh_evento:
        return 'Evento de Software', True
    elif eh_tech:
        return 'Tecnologia', True
    elif eh_evento:
        return 'Evento', False
    
    return 'Geral', False

def monitorar_homepage():
    url_homepage = "https://www4.unievangelica.edu.br/" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    conn = None
    cursor = None

    try:
        response = requests.get(url_homepage, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. PASSO DE LIMPEZA: Elimina elementos de navegação e estrutura antes de buscar artigos
        for lixo in soup.select('nav, footer, header, aside, .menu, .sidebar, .footer, .btn, .botao, .atendimento'):
            lixo.decompose()

        # 2. SELEÇÃO DE ARTIGOS
        artigos = soup.select('article, div.noticia, .post-item, .card, a[href*="noticia"]')

        conn = obter_conexao()
        cursor = conn.cursor()
        novas_noticias = 0
        links_processados = set()

        # 3. FILTRAGEM E VALIDAÇÃO DOS ITENS
        for item in artigos:
            link_tag = item if item.name == 'a' else item.find('a')
            if not link_tag or not link_tag.get('href'):
                continue

            # Limpa o texto tirando espaços extras/quebras de linha internas
            titulo_raw = " ".join(link_tag.get_text(strip=True).split())
            
            # Insere espaço entre letras e números grudados (ex: "Anápolis16º" -> "Anápolis 16º")
            titulo = re.sub(r'([a-zA-ZáàâãéèêíóôõúçÁÀÂÃÉÈÊÍÓÔÕÚÇ])(\d+º?)', r'\1 \2', titulo_raw)
            
            link_bruto = link_tag['href'].strip()

            # Ignora títulos curtos/vazios
            if not titulo or len(titulo) < 15:
                continue

            # Trava contra termos institucionais e botões soltos
            titulo_lc = titulo.lower()
            if any(termo in titulo_lc for termo in KEYWORDS_IGNORAR):
                continue

            # Trata URLs relativas/absolutas corretamente
            link = urljoin(url_homepage, link_bruto)

            # Evita reprocessar o mesmo link no mesmo ciclo
            if link in links_processados:
                continue
            links_processados.add(link)

            categoria, eh_relevante = classificar_noticia(titulo)

            sql = """
                INSERT IGNORE INTO noticias (titulo, link, categoria, eh_relevante) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (titulo, link, categoria, eh_relevante))
            
            if cursor.rowcount > 0:
                novas_noticias += 1

        conn.commit()
        print(f"[FoxxPI Scraper] Homepage varrida com sucesso. Novas entradas: {novas_noticias}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[FoxxPI Scraper] Erro durante a varredura da homepage: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    monitorar_homepage()