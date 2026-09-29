import re
import requests
from bs4 import BeautifulSoup
from database import obter_conexao

# Listas de palavras-chave para filtro
KEYWORDS_TECH = [
    'tecnologia', 'programação', 'desenvolvimento', 'software', 'ti', 
    'inteligência artificial', 'ia', 'python', 'javascript', 'algoritmo',
    'computação', 'hackathon', 'maratona', 'dados', 'cybersecurity', 'sistema'
]

KEYWORDS_EVENTOS = [
    'evento', 'workshop', 'palestra', 'semana acadêmica', 'webinar',
    'simpósio', 'conferência', 'inscrições abertas', 'minicurso', 'meetup'
]

def classificar_noticia(titulo):
    """Analisa o título e classifica por relevância e categoria."""
    titulo_lc = titulo.lower()
    
    eh_tech = any(re.search(rf'\b{kw}\b', titulo_lc) for kw in KEYWORDS_TECH)
    eh_evento = any(re.search(rf'\b{kw}\b', titulo_lc) for kw in KEYWORDS_EVENTOS)
    
    if eh_tech and eh_evento:
        return 'Evento de Software', True
    elif eh_tech:
        return 'Tecnologia', True
    elif eh_evento:
        return 'Evento', False
    
    return 'Geral', False

def monitorar_homepage():
    # 1. URL da HOMEPAGE da faculdade
    url_homepage = "https://www4.unievangelica.edu.br/" 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url_homepage, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. CAPTURA DE LINKS DA HOMEPAGE
        # Procuramos por tags <a> que tenham texto relevante (evitando links de menu/rodapé vazios)
        links = soup.find_all('a', href=True)

        conn = obter_conexao()
        cursor = conn.cursor()
        novas_noticias = 0

        for link_tag in links:
            titulo = link_tag.get_text(strip=True)
            link = link_tag['href']

            # Filtro básico para ignorar links curtos ou botões do menu principal (ex: "Home", "Contato", "Entrar")
            if len(titulo) < 15:
                continue

            # Ajusta links relativos para URLs completas (ex: "/noticias/1" -> "https://faculdade.edu.br/noticias/1")
            if not link.startswith('http'):
                link = f"{url_homepage.rstrip('/')}/{link.lstrip('/')}"

            categoria, eh_relevante = classificar_noticia(titulo)

            sql = """
                INSERT IGNORE INTO noticias (titulo, link, categoria, eh_relevante) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (titulo, link, categoria, eh_relevante))
            
            if cursor.rowcount > 0:
                novas_noticias += 1

        conn.commit()
        cursor.close()
        conn.close()

        print(f"[FoxxPI Scraper] Homepage varrida com sucesso. Novas entradas: {novas_noticias}")

    except Exception as e:
        print(f"[FoxxPI Scraper] Erro durante a varredura da homepage: {e}")

if __name__ == "__main__":
    monitorar_homepage()