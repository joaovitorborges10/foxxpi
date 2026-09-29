const API_URL = 'http://localhost:5000/api/noticias';

async function carregarNoticias(queryParams = 'relevantes=true') {
    const container = document.getElementById('news-container');
    container.innerHTML = '<p class="loading">Buscando notícias no FoxxPI...</p>';

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
            if (item.categoria.includes('Evento')) badgeClass = 'badge-evento';

            const dataFormatada = new Date(item.capturado_em).toLocaleString('pt-BR');

            card.innerHTML = `
                <span class="badge ${badgeClass}">${item.categoria}</span>
                <h3>
                    <a href="${item.link}" target="_blank" rel="noopener noreferrer">${item.titulo}</a>
                </h3>
                <div class="meta">Capturado em: ${dataFormatada}</div>
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error('Erro na requisição:', error);
        container.innerHTML = '<p class="loading" style="color:#ef4444;">Erro ao conectar com a API do FoxxPI.</p>';
    }
}

function filtrar(queryParams, botao) {
    // Atualiza o estado dos botões
    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    botao.classList.add('active');

    carregarNoticias(queryParams);
}

// Inicializa buscando conteúdos de Tecnologia e Eng. de Software por padrão
document.addEventListener('DOMContentLoaded', () => carregarNoticias('relevantes=true'));