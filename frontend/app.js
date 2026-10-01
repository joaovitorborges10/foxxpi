const hostname = window.location.hostname;
let API_BASE;

if (hostname.includes('vercel.app')) {
  API_BASE = "https://joao-desktop.tailddbe06.ts.net"; 
} else if (hostname === 'localhost' || hostname === '127.0.0.1') {
  API_BASE = "http://localhost:5000";                
} else {
  API_BASE = "http://100.83.84.41:5000";             
}

const API_URL = `${API_BASE}/api/noticias`;
let filtroAtual = 'relevantes=true';

function formatarDataSegura(dataValor) {
    if (!dataValor || dataValor === 'null') return 'Data não informada';

    if (typeof dataValor === 'string' && dataValor.includes('/')) {
        return dataValor;
    }

    if (typeof dataValor === 'string' && dataValor.includes('-')) {
        const apenasData = dataValor.split('T')[0];
        const partes = apenasData.split('-');
        if (partes.length === 3) {
            const [ano, mes, dia] = partes;
            return `${dia}/${mes}/${ano}`;
        }
    }

    const dataObj = new Date(dataValor);
    if (!isNaN(dataObj.getTime())) {
        return dataObj.toLocaleDateString('pt-BR');
    }

    return 'Data não informada';
}

async function carregarNoticias(queryParams = filtroAtual, silencioso = false) {
    const container = document.getElementById('news-container');
    
    if (!silencioso) {
        container.innerHTML = '<p class="loading">Buscando notícias no FoxxPI...</p>';
    }

    try {
        const response = await fetch(`${API_URL}?${queryParams}`);
        const noticias = await response.json();

        container.innerHTML = '';

        if (noticias.length === 0) {
            container.innerHTML = '<p class="loading">Nenhuma notícia encontrada para este filtro.</p>';
            return;
        }

        noticias.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card';

            let badgeClass = 'badge-geral';
            if (item.categoria === 'Tecnologia') badgeClass = 'badge-tech';
            if (item.categoria && item.categoria.includes('Evento')) badgeClass = 'badge-evento';

            const dataExibicao = formatarDataSegura(item.data_publicacao || item.criado_em);

            card.innerHTML = `
                <span class="badge ${badgeClass}">${item.categoria || 'Geral'}</span>
                <h3>
                    <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.titulo}</a>
                </h3>
                <div class="meta">Publicado em: ${dataExibicao}</div>
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error('Erro na requisição:', error);
        if (!silencioso) {
            container.innerHTML = '<p class="loading" style="color:#ef4444;">Erro ao conectar com a API do FoxxPI.</p>';
        }
    }
}

function filtrar(queryParams, botao) {
    filtroAtual = queryParams;
    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    botao.classList.add('active');
    carregarNoticias(queryParams, false);
}

document.addEventListener('DOMContentLoaded', () => {
    carregarNoticias(filtroAtual, false);
    setInterval(() => {
        carregarNoticias(filtroAtual, true);
    }, 30000);
});