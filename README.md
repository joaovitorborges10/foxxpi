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
│   ├── database.py                 # Conexão com a base de dados
│   ├── main.py                     # API REST para servir os dados ao frontend
│   └── scraper.py                  # Script de raspagem e persistência de dados
├── frontend/
│   ├── index.html                  # Interface do utilizador
│   ├── app.js                      # Consumo da API e atualização em tempo real
│   └── style.css                   # Estilização do painel de notícias
├── foxxpi_database_schema.sql      # Estrutura e tabelas do MySQL
├── run_scraper.sh                  # Script de automação e gestão de processos
├── requirements.txt                # Dependências do ecossistema Python
├── logo.png                        # Identidade visual / Social Preview
└── README.md                       # Documentação do repositório
