# 🦊 FoxxPI

> Um agente simples de raspagem de dados (*web scraping*) escrito em Python para monitorar notícias e avisos do *campus* da UniEVANGÉLICA.

---

## 📋 Sobre o Projeto

O **FoxxPI** é um projeto de automação desenvolvido para capturar e centralizar notícias, eventos e comunicados do ecossistema da UniEVANGÉLICA. O sistema opera em segundo plano, filtrando informações relevantes e disponibilizando-as numa interface web simples com atualização em tempo real.

---

## 🛠️ Arquitetura e Tecnologias

- **Linguagem:** Python 3
- **Base de Dados:** MySQL (`foxxpi_database`)
- **Backend / API:** Flask
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API + Polling)
- **Automação:** Shell Scripting (`bash`) e `cron` no Linux

---

## 🚀 Como Executar

Para colocar o projeto em funcionamento em um ambiente **Linux**, certifique-se de que possui as ferramentas pré-requisitas instaladas:
- **Docker** e **Docker Compose**
- **Python 3 / Pip**
- **Tailscale** configurado
- *(Opcional)* Vercel CLI via `npm` (ferramenta usada opcionalmente apenas para fins de deploy/serverless, sem ligação direta com a execução local do projeto).

Siga os passos abaixo no terminal:

1. Clone o repositório e navegue até a pasta do projeto:
   ```bash
   git clone <url-do-repositorio>
   cd foxxpi
   ```
2. Dê permissão de execução ao script orquestrador (caso necessário):
   ```bash
   chmod +x run_scraper.sh
   ```
3. Execute o script orquestrador para iniciar os serviços (Docker, Banco de Dados, Backend, Funnel, Frontend e Scraper) e acompanhe os logs gerados:
   ```bash
   ./run_scraper.sh
   ```
4. Acesse a aplicação no navegador em **`http://localhost:8080`** para visualizar o painel, testar o sistema e realizar eventuais debuggings.

---

## ⚙️ Estrutura do Projeto

```text
foxxpi/
├── api/
│   └── index.py                    # Serverless Function / Entrypoint de redirecionamento para a Vercel
├── backend/
│   ├── database.py                 # Conexão e gerenciamento do pool do MySQL
│   ├── main.py                     # API REST (Flask) para servir os endpoints de notícias
│   └── scraper.py                  # Engine de raspagem, parsing e persistência de dados
├── frontend/
│   ├── index.html                  # Interface web (Single Page Application)
│   ├── app.js                      # Consumo da API, comutação de ambiente e auto-refresh
│   └── style.css                   # Estilização responsiva do painel de notícias
├── database_autodelete_cron.sql    # Event Scheduler do MySQL para purga automática de dados
├── docker-compose.yml              # Orquestração do container MySQL com o agendador nativo ativo
├── foxxpi_database_schema.sql      # Schema de tabelas e índices da base de dados
├── run_scraper.sh                  # Orquestrador de processos (Docker, DB, Backend, Funnel, Frontend e Scraper)
├── requirements.txt                # Dependências Python do projeto
├── vercel.json                     # Configuração de rotas e build serverless da Vercel
├── logo.png                        # Identidade visual e marca do FoxxPI
└── README.md                       # Documentação do repositório
```