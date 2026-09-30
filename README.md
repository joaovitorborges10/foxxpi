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
## ⚙️ Estrutura do Projeto

```text
foxxpi/
├── backend/
│   ├── database.py                 # Conexão e gerenciamento do pool do MySQL
│   ├── main.py                     # API REST (Flask) para servir os endpoints de notícias
│   └── scraper.py                  # Engine de raspagem, parsing e persistência de dados
├── frontend/
│   ├── index.html                  # Interface web (Single Page Application)
│   ├── app.js                      # Consumo da API, comutação de ambiente e auto-refresh
│   └── style.css                   # Estilização responsiva do painel de notícias
├── database_autodelete_cron.sql    # Event Scheduler do MySQL para purga automática
├── foxxpi_database_schema.sql      # Schema de tabelas e índices da base de dados
├── run_scraper.sh                  # Orquestrador de processos (Backend, Funnel, Frontend e Scraper)
├── requirements.txt                # Dependências Python do projeto
├── logo.png                        # Identidade visual e marca do FoxxPI
└── README.md                       # Documentação do repositório
