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
- **Automação:** Shell Scripting (`bash`) e `systemd` no Linux

## 🚀 Como Executar

Para colocar o projeto em funcionamento certifique-se de ter um ambiente Linux ou Windows 10 e Posteriores via _(Windows Subsystem for Linux)_ e todas as dependências listadas abaixo:
- `docker.io` / `docker-compose-v2`
- `python3-venv` / `python3-pip` / `libnotify-bin`
- `vercel-cli` / `taiscale` *(Opcional)*

## 🔧 Configuração

Siga os passos abaixo no terminal:

1. Clone o repositório e navegue até a pasta do projeto:
   ```bash
   # Onde deseja alocar o Agente.
   git clone https://github.com/joaovitorborges10/foxxpi.git
   cd foxxpi
   ```
2. Dê permissão e execute o script de autoconfiguração:
   ```bash
   # Instalação
   chmod +x *.sh
   ./install_scraper.sh
   ```
> Acesse a aplicação no navegador em **`http://localhost:8080`** para visualizar o painel, testar o sistema e realizar eventuais debuggings.

## 🚫 Gerenciamento de Processos e Reset Completo do Ambiente

O Ambiente do FoxxPI é Integrado ao SystemD por Padrão e pode Usufruir de Comandos Nativos como:

- Verificar Estado e Logs com: ```systemctl status foxxpi.service```
- Encerrar o Agente com: ```systemctl stop foxxpi.service```
- Iniciar Manualmente o Agente com: ```systemctl start foxxpi.service```
- Habilita-lo na Inicialização do Sistema com: ```systemctl enable foxxpi.service```
  
> Lembrando que toda a Configuração e Ativação do Daemon é Automatizada via _install_scraper.sh_ conforme especificado nos passos anteriores desse _README.md_

---

2. Alternativamente é Possível Forçar o Encerramento dos Serviços e do Daemon _foxxpi.service_ através do script nativo _stop_services.sh_ como no exemplo abaixo:
```bash
# Encerrar Serviços
./stop_services.sh
 ```

3. Mesma Lógica se Aplica ao Script _reset_all.sh_ para Reverter a Instalação e **DESTRUIR** o Container MySQL e o Banco de Dados:
```bash
# Reverter Ações do FoxxPI
./reset_all.sh
 ``` 
## ⚙️  Estrutura do Projeto

 ```text 
foxxpi/
├── api/
│   └── index.py                     # Serverless Function / Entrypoint de redirecionamento para a Vercel
├── backend/
│   ├── database.py                  # Conexão e gerenciamento do pool do MySQL
│   ├── main.py                      # API REST (Flask) para servir os endpoints de notícias
│   └── scraper.py                   # Engine de raspagem, parsing e persistência de dados
├── frontend/
│   ├── index.html                   # Interface web (Single Page Application)
│   ├── app.js                       # Consumo da API, comutação de ambiente e auto-refresh
│   └── style.css                    # Estilização responsiva do painel de notícias
├── database_autodelete_cron.sql     # Event Scheduler do MySQL para purga automática de dados
├── docker-compose.yml               # Orquestração do container MySQL com o agendador nativo ativo
├── foxxpi_database_schema.sql       # Schema de tabelas e índices da base de dados
├── foxxpi.service                   # Unit file padrão do systemd
├── install_scrapper.sh              # Script global interativo de setup do daemon (Systemd)
├── scraper.sh                       # Orquestrador de processos para Linux Padrão
├── scraper_full_deploy.sh           # Orquestrador de processos para Linux Full Deploy / Servidor
├── scraper_wsl.sh                   # Orquestrador de processos para WSL
├── stop_services.sh                 # Script para paragem segura dos serviços nas portas 5000 e 8080
├── reset_all.sh                     # Script para reset total (systemd, funnel, portas, docker e logs)
├── requirements.txt                 # Dependências Python do projeto
├── vercel.json                      # Configuração de rotas e build serverless da Vercel
├── logo.png                         # Identidade visual e marca do FoxxPI
└── README.md                        # Documentação do repositório
 ``` 
