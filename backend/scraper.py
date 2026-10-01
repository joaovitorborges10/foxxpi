import re
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from database import obter_conexao
import os
import subprocess

ddef enviar_notificacao(titulo, mensagem):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [Notificação] Tentando enviar: '{titulo}' -> '{mensagem}'")
    
    try:
        wrapper_local = os.path.expanduser("~/.local/bin/notify-send")
        
        if os.path.exists(wrapper_local) and os.access(wrapper_local, os.X_OK):
            cmd = wrapper_local
        elif os.path.exists("/usr/bin/notify-send"):
            cmd = "/usr/bin/notify-send"
        else:
            cmd = "notify-send"

        # Garante o ambiente do D-Bus e Display para o subprocesso
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={env['XDG_RUNTIME_DIR']}/bus"

        resultado = subprocess.run(
            [cmd, titulo, mensagem],
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
        print(f"[{timestamp}] [Notificação] Sucesso via {cmd}: {resultado.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[{timestamp}] [Notificação] ERRO (CalledProcessError): {e.stderr.strip()}")
    except Exception as e:
        print(f"[{timestamp}] [Notificação] ERRO Inesperado: {e}")

URL_NOTICIAS = "https://www4.unievangelica.edu.br/noticia"
DATA_CORTE = datetime(2026, 8, 1)

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

        for lixo in soup.select('nav, footer, header, aside, .menu, .sidebar, .footer, .btn, .botao, .atendimento'):
            lixo.decompose()

        artigos = soup.select('article, div.noticia, .post-item, .card, a[href*="noticia"]')

        conn = obter_conexao()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM noticias")
        total_registos_bd = cursor.fetchone()[0]
        primeira_execucao = (total_registos_bd == 0)

        noticias_processadas = 0
        links_processados = set()
        candidatas_primeiro_boot = []

        for item in artigos:
            if noticias_processadas >= 20:
                break

            link_tag = item if item.name == 'a' else item.find('a')
            if not link_tag or not link_tag.get('href'):
                continue

            data_noticia = None
            
            tag_tempo = item.find('time') or item.find(class_=re.compile('data|date|time', re.IGNORECASE))
            if tag_tempo:
                match_data = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', tag_tempo.get_text(strip=True))
                if match_data:
                    data_noticia = parse_data(match_data.group(1))

            if not data_noticia:
                for sub_elem in item.find_all(['span', 'div', 'p', 'li', 'td']):
                    texto_elem = sub_elem.get_text(strip=True)
                    match_data = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', texto_elem)
                    if match_data:
                        data_parseada = parse_data(match_data.group(1))
                        if data_parseada and data_parseada <= datetime.now():
                            data_noticia = data_parseada
                            break

            titulo_raw = link_tag.get_text(separator=' ', strip=True)
            if not data_noticia:
                match_data_titulo = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', titulo_raw)
                if match_data_titulo:
                    data_noticia = parse_data(match_data_titulo.group(1))
                    titulo_raw = titulo_raw.replace(match_data_titulo.group(1), '').strip()

            if not data_noticia:
                data_noticia = datetime.now()

            if data_noticia < DATA_CORTE:
                continue

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

            if "tecnologia-em-transformacao-aws-tech-day" in link.lower():
                titulo = "Tecnologia em transformação: AWS Tech Day Anápolis discute IA, nuvem e escalabilidade"

            titulo_lc = titulo.lower()
            if any(termo in titulo_lc for termo in KEYWORDS_IGNORAR):
                continue

            if link in links_processados:
                continue
            links_processados.add(link)

            categoria, eh_relevante = classificar_noticia(titulo)
            data_sql = data_noticia.strftime("%Y-%m-%d")

            sql = """
                INSERT INTO noticias (titulo, link, categoria, eh_relevante, data_publicacao) 
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    titulo = VALUES(titulo),
                    categoria = VALUES(categoria),
                    eh_relevante = VALUES(eh_relevante),
                    data_publicacao = VALUES(data_publicacao)
            """
            cursor.execute(sql, (titulo, link, categoria, eh_relevante, data_sql))
            
            if primeira_execucao and eh_relevante:
                candidatas_primeiro_boot.append(titulo)
            
            if not primeira_execucao and cursor.rowcount == 1 and eh_relevante:
                enviar_notificacao("FoxxPI - Nova Notícia", titulo)

            noticias_processadas += 1

        conn.commit()

        if primeira_execucao and candidatas_primeiro_boot:
            ultima_relevante = candidatas_primeiro_boot[-1]
            enviar_notificacao("FoxxPI - Inicialização", ultima_relevante)

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