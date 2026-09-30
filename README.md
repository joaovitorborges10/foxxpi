# 🦊 FoxxPI

> Um agente simples de raspagem de dados (*web scraping*) escrito em Python para monitorar notícias e avisos do *campus* da UniEVANGÉLICA.

## 🛠️  Arquitetura e Tecnologias

- **Linguagem:** Python 3
- **Base de Dados:** MySQL (`foxxpi_database`)
- **Backend / API:** Flask
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API + Polling)
- **Automação:** Shell Scripting (`bash`) e `cron` no Linux

## 🚀 Como Executar

Para colocar o projeto em funcionamento em um ambiente **Linux**, certifique-se de que possui as ferramentas pré-requisitas instaladas:
- **Docker** e **Docker Compose**
- **Python 3 / Pip**
- **Tailscale** configurado
- *(Opcional)* Vercel CLI via `npm` (ferramenta usada opcionalmente apenas para fins de deploy/serverless, sem ligação direta com a execução local do projeto).

## 🔧 Configuração

Siga os passos abaixo no terminal:

1. Clone o repositório e navegue até a pasta do projeto:
   ```bash
   git clone <url-do-repositorio>
   cd foxxpi
   ```
2. Dê permissão de execução ao script de arranque (caso necessário):
   ```bash
   chmod +x run_scraper.sh
   ```
3. Execute o script de arranque para iniciar os serviços (Docker, Banco de Dados, Backend, Funnel, Frontend e Scraper) e acompanhe os logs gerados:
   ```bash
   ./run_scraper.sh
   ```
4. Acesse a aplicação no navegador em **`http://localhost:8080`** para visualizar o painel, testar o sistema e realizar eventuais debuggings.

## 🚫 Encerramento de Processos e Reset Completo do Ambiente

6. Caso Seja Necessário o Encerramento dos processos utilize o script (stop_services.sh)
  ```bash
   chmod +x stop_services.sh
   ./stop_services.sh
  ```

7. Para Eliminar todo o Serviço incluindo DESTRUIR o Container SQL utilize o script (reset_all.sh)
  ```bash
   chmod +x stop_services.sh
   ./reset_all.sh
   ```

## ⚙️  Estrutura do Projeto

 ```text 
foxxpi/
├── api/
│   └── index.py                    # Serverless Function / Entrypoint de redirecionamento para a Vercel[cite: 3]
├── backend/
│   ├── database.py                 # Conexão e gerenciamento do pool do MySQL[cite: 3]
│   ├── main.py                     # API REST (Flask) para servir os endpoints de notícias[cite: 3]
│   └── scraper.py                  # Engine de raspagem, parsing e persistência de dados[cite: 3]
├── frontend/
│   ├── index.html                  # Interface web (Single Page Application)[cite: 3]
│   ├── app.js                      # Consumo da API, comutação de ambiente e auto-refresh[cite: 3]
│   └── style.css                   # Estilização responsiva do painel de notícias[cite: 3]
├── database_autodelete_cron.sql    # Event Scheduler do MySQL para purga automática de dados[cite: 3]
├── docker-compose.yml              # Orquestração do container MySQL com o agendador nativo ativo[cite: 3]
├── foxxpi_database_schema.sql      # Schema de tabelas e índices da base de dados[cite: 3]
├── run_scraper.sh                  # Orquestrador de processos (Docker, DB, Backend, Funnel, Frontend e Scraper)[cite: 3]
├── stop_services.sh                # Script para paragem segura dos serviços nas portas 5000 e 8080
├── reset_all.sh                    # Script para reset total do ambiente e limpeza do banco de dados
├── requirements.txt                # Dependências Python do projeto[cite: 3]
├── vercel.json                     # Configuração de rotas e build serverless da Vercel[cite: 3]
├── logo.png                        # Identidade visual e marca do FoxxPI[cite: 3]
└── README.md                       # Documentação do repositório[cite: 3]
 ``` 
