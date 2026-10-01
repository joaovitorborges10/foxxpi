import re
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from database import obter_conexao
import subprocess

# URL de destino
URL_NOTICIAS = "https://www4.unievangelica.edu.br/noticia"

# Data limite para filtro: 01 de Agosto de 2026
DATA_CORTE = datetime(2026, 8, 1)

# Listas de palavras-chave para filtro (com termos compostos seguros)
KEYWORDS_TECH = [
    'tecnologia', 'programação', 'desenvolvimento', 'software', 'ti', 
    'inteligência artificial', 'ia', 'python', 'javascript', 'algoritmo',
    'computação', 'hackathon', 'maratona', 'dados', 'cybersecurity', 'sistema',
    'engenharia de software', 'sistemas de informação', 'ciência da computação',
    'análise e desenvolvimento', 'inovação', 'ciência', 'transformação digital'
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
    """Verifica se alguma palavra-chave ou termo composto está presente no texto."""
    for kw in keywords:
        if ' ' in kw:
            if kw in texto:
                return True
        else:
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

def enviar_notificacao_desktop(titulo):
    """Dispara a notificação nativa no Linux via libnotify."""
    try:
        subprocess.run(["notify-send", "🦊 FoxxPI - Nova Notícia", titulo], check=True)
    except Exception as e:
        print(f"[FoxxPI] Erro ao enviar notificação: {e}")

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

        cursor.execute("SELECT COUNT(*) FROM noticias")
        total_registos_bd = cursor.fetchone()[0]
        primeira_execucao = (total_registos_bd == 0)

        noticias_processadas = 0
        links_processados = set()
        primeira_noticia_relevante_titulo = None

        # 3. Filtragem, limite de 20 e gravação
        for item in artigos:
            if noticias_processadas >= 20:
                break

            link_tag = item if item.name == 'a' else item.find('a')
            if not link_tag or not link_tag.get('href'):
                continue

            data_noticia = None
            span_encontrado = None
            for span in item.find_all(['span', 'time', 'p', 'div']):
                texto_span = span.get_text(strip=True)
                match_data = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', texto_span)
                if match_data:
                    data_noticia = parse_data(match_data.group(1))
                    span_encontrado = span
                    break

            if data_noticia and data_noticia < DATA_CORTE:
                continue

            if span_encontrado:
                span_encontrado.decompose()

            titulo_raw = link_tag.get_text(separator=' ', strip=True)

            titulo_tratado = re.sub(r'([a-zà-ú])([A-ZÀ-Ú])', r'\1 \2', titulo_raw)
            titulo_tratado = re.sub(r'\bUni\s+EVANGÉLICA\b', 'UniEVANGÉLICA', titulo_tratado, flags=re.IGNORECASE)
            titulo_tratado = re.sub(r'\bUni\s+EVANGELICA\b', 'UniEVANGÉLICA', titulo_tratado, flags=re.IGNORECASE)
            titulo = re.sub(r'([a-zA-ZáàâãéèêíóôõúçÁÀÂÃÉÈÊÍÓÔÕÚÇ])(\d+º?)', r'\1 \2', titulo_tratado)
            titulo = " ".join(titulo.split())

            titulo = re.sub(r'^(Todos os Campi|Campus [A-Za-zÀ-Ú\s]+)\s*-\s*', '', titulo, flags=re.IGNORECASE)
            titulo = re.sub(r'^(Todos os Campi|Campus [A-Za-zÀ-Ú\s]+)\s+', '', titulo, flags=re.IGNORECASE)

            if not titulo or len(titulo) < 15 or re.fullmatch(r'Campus\s+[A-Za-zÀ-Ú\s]+|Todos os Campi', titulo, flags=re.IGNORECASE):
                continue

            link_bruto = link_tag['href'].strip()
            link = urljoin(URL_NOTICIAS, link_bruto)

            # 🔥 Correção pontual para o título do AWS Tech Day que vem cortado do card HTML
            if "tecnologia-em-transformacao-aws-tech-day" in link.lower():
                titulo = "Tecnologia em transformação: AWS Tech Day Anápolis discute IA, nuvem e escalabilidade"

            titulo_lc = titulo.lower()
            if any(termo in titulo_lc for termo in KEYWORDS_IGNORAR):
                continue

            if link in links_processados:
                continue
            links_processados.add(link)

            categoria, eh_relevante = classificar_noticia(titulo)
            data_sql = data_noticia.strftime("%Y-%m-%d") if data_noticia else None

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
            
            if primeira_execucao and eh_relevante and not primeira_noticia_relevante_titulo:
                primeira_noticia_relevante_titulo = titulo
            
            if not primeira_execucao and cursor.rowcount == 1 and eh_relevante:
                enviar_notificacao_desktop(titulo)

            noticias_processadas += 1

        conn.commit()

        if primeira_execucao and primeira_noticia_relevante_titulo:
            enviar_notificacao_desktop(f"[Inicialização] {primeira_noticia_relevante_titulo}")

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