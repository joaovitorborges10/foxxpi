const API_URL = 'http://localhost:5000/api/noticias';

// Guarda o filtro ativo para manter a escolha do utilizador na atualização automática
let filtroAtual = 'relevantes=true';

async function carregarNoticias(queryParams = filtroAtual, silencioso = false) {
    const container = document.getElementById('news-container');
    
    // Só mostra o texto de carregamento na primeira busca ou ao clicar num botão
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

            // Escolhe a classe da tag visual
            let badgeClass = 'badge-geral';
            if (item.categoria === 'Tecnologia') badgeClass = 'badge-tech';
            if (item.categoria && item.categoria.includes('Evento')) badgeClass = 'badge-evento';

            const dataFormatada = new Date(item.capturado_em).toLocaleString('pt-BR');

            card.innerHTML = `
                <span class="badge ${badgeClass}">${item.categoria || 'Geral'}</span>
                <h3>
                    <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.titulo}</a>
                </h3>
                <div class="meta">Capturado em: ${dataFormatada}</div>
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
    // Guarda o novo filtro ativo
    filtroAtual = queryParams;

    // Atualiza o estado visual dos botões
    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    botao.classList.add('active');

    // Executa a busca visível (com indicação de carregamento)
    carregarNoticias(queryParams, false);
}

// Inicializa o script quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    // 1. Busca inicial
    carregarNoticias(filtroAtual, false);

    // 2. Atualização automática em segundo plano a cada 30 segundos (30000 ms)
    setInterval(() => {
        carregarNoticias(filtroAtual, true);
    }, 30000);
});