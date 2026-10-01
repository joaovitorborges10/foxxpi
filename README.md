![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-green?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containers-blue?logo=docker&logoColor=white)
# 🦊 FoxxPI

> Um agente simples de raspagem de dados (*web scraping*) escrito em Python para monitorar notícias e avisos do *campus* da UniEVANGÉLICA.

## 🛠️  Arquitetura e Tecnologias

- **Linguagem:** Python 3
- **Base de Dados:** MySQL (`foxxpi_database`)
- **Backend / API:** Flask
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API + Polling)
- **Automação:** Shell Scripting (`bash`) e `cron` no Linux

## 🚀 Como Executar

Para colocar o projeto em funcionamento em um ambiente **Linux**, certifique-se de que possui todas as dependências instaladas:
- **Docker** e **Docker Compose**
- **Python 3 / Pip**
- **libnotify-bin /** _Instalado previamente através do package manager da sua distribuição._
- **Tailscale** configurado
- *(Opcional)* Vercel CLI via `npm` (ferramenta usada opcionalmente apenas para fins de deploy/serverless, sem ligação direta com a execução local do projeto).

## 🔧 Configuração

Siga os passos abaixo no terminal:

1. Clone o repositório e navegue até a pasta do projeto:
   ```bash
   git clone https://github.com/joaovitorborges10/foxxpi.git
   cd foxxpi
   ```
2. Dê permissão de execução ao script de arranque (caso necessário):
   ```bash
   # Linux
   chmod +x run_scraper.sh

   # WSL
   chmod +x run_scraper_wsl.sh
   ```
3. Execute o script de arranque para iniciar os serviços (Docker, Banco de Dados, Backend, Funnel, Frontend e Scraper) e acompanhe os logs gerados:
   ```bash
   # Linux
   ./run_scraper.sh

   # WSL
   ./run_scraper_wsl.sh
   ```
> Acesse a aplicação no navegador em **`http://localhost:8080`** para visualizar o painel, testar o sistema e realizar eventuais debuggings.

## 🚫 Encerramento de Processos e Reset Completo do Ambiente

1. Caso seja necessário o encerramento dos processos utilize o script **stop_services.sh**
  ```bash
   chmod +x stop_services.sh
   ./stop_services.sh
  ```

2. Para **ELIMINAR** todo o serviço incluindo **DESTRUIR** o Banco de Dados utilize o script **reset_all.sh**
  ```bash
   chmod +x reset_all.sh
   ./reset_all.sh
   ```
> Também podendo ser utilizado para regenerar o ambiente em eventuais incoerências e recriar o ecossistema como um todo a partir dos passos especificados nas guias anteriores desse README.md

## ⚙️  Estrutura do Projeto

 ```text 
foxxpi/
├── api/
│   └── index.py                    # Serverless Function / Entrypoint de redirecionamento para a Vercel
├── backend/
│   ├── database.py                 # Conexão e gerenciamento do pool do MySQL
│   ├── main.py                     # API REST (Flask) para servir os endpoints de notícias
│   └── scraper.py                  # Engine de raspagem, parsing e persistência de dados
├── frontend/
│   ├── index.html                  # Interface web (Single Page Application)
│   ├── app.js                      # Consumo da API, comutação de ambiente e auto-refresh
│   └── style.css                   # Estilização responsiva do painel de notícias
├── database_autodelete_cron.sql    # Event Scheduler do MySQL para purga automática de dados
├── docker-compose.yml              # Orquestração do container MySQL com o agendador nativo ativo
├── foxxpi_database_schema.sql      # Schema de tabelas e índices da base de dados
├── run_scraper.sh                  # Orquestrador de processos (Docker, DB, Backend, Funnel, Frontend e Scraper)
├── stop_services.sh                # Script para paragem segura dos serviços nas portas 5000 e 8080
├── reset_all.sh                    # Script para reset total do ambiente e limpeza do banco de dados
├── requirements.txt                # Dependências Python do projeto
├── vercel.json                     # Configuração de rotas e build serverless da Vercel
├── logo.png                        # Identidade visual e marca do FoxxPI
└── README.md                       # Documentação do repositório
 ``` 
