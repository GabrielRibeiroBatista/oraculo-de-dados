# Oráculo de Dados

Sistema de web scraping e dashboard para coleta e visualização de dados de múltiplas fontes.

![Oráculo de Dados](docs/images/logo.png)

## 📋 Sobre o Projeto

O Oráculo de Dados é um sistema completo para coleta automatizada de dados da web (web scraping) e visualização em um dashboard interativo. O sistema monitora sites de notícias, redes sociais públicas, blogs, fóruns e outras fontes, coletando informações com base em palavras-chave configuráveis.

### Principais Funcionalidades

- **Web Scraping Customizável**: Configure fontes e palavras-chave para monitoramento
- **Agendamento Automático**: Execute coletas em intervalos programados
- **Dashboard Interativo**: Visualize os dados coletados com gráficos e tabelas
- **Painel Administrativo**: Gerencie fontes, palavras-chave e monitore o histórico de coletas
- **100% Compatível com Windows**: Desenvolvido para funcionar perfeitamente em Windows 11

## 🧱 Tecnologias Utilizadas

### Back-End
- **Framework**: Django (Python)
- **Banco de dados**: SQLite3
- **Web Scraping**: BeautifulSoup4, Requests, Selenium
- **Agendamento**: APScheduler (compatível com Windows)

### Front-End
- **HTML5 + CSS3**
- **JavaScript** (integrado nos templates Django)
- **Chart.js** para visualizações gráficas
- **Bootstrap** para interface responsiva

## 🚀 Instalação e Configuração

### Pré-requisitos
- Windows 10 ou 11
- Python 3.10 ou superior
- Navegador Chrome (para Selenium, quando necessário)

### Instalação Rápida (Windows)

1. Clone ou baixe este repositório
2. Execute o script de configuração automática:
   ```
   configurar_windows.bat
   ```
3. Siga as instruções na tela para criar um superusuário administrador
4. Inicie o servidor:
   ```
   python manage.py runserver
   ```
5. Acesse o sistema em: http://127.0.0.1:8000/

### Instalação Manual

1. Clone ou baixe este repositório
2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   ```
   venv\Scripts\activate
   ```
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
5. Execute as migrações do banco de dados:
   ```
   python manage.py migrate
   ```
6. Crie um superusuário:
   ```
   python manage.py createsuperuser
   ```
7. Inicie o servidor:
   ```
   python manage.py runserver
   ```
8. Acesse o sistema em: http://127.0.0.1:8000/

## 📊 Estrutura do Projeto

O projeto está organizado em três aplicações Django:

- **scraper**: Responsável pela coleta de dados
  - Modelos: Fonte, PalavraChave, EntradaColetada
  - Sistema de scraping com BeautifulSoup4 e Selenium
  - Agendamento de tarefas com APScheduler

- **dashboard**: Visualização pública dos dados
  - Dashboard principal com gráficos e estatísticas
  - Tabelas ordenáveis e filtros avançados
  - Visualizações detalhadas por fonte e palavra-chave

- **administrativo**: Gestão do sistema
  - Autenticação de usuários
  - Gerenciamento de fontes e palavras-chave
  - Visualização de logs e histórico de coletas

## 🔄 Uso do Sistema

### Painel Administrativo

1. Acesse http://127.0.0.1:8000/administrativo/
2. Faça login com as credenciais de superusuário
3. No painel administrativo, você pode:
   - Gerenciar fontes de dados
   - Configurar palavras-chave para monitoramento
   - Visualizar o histórico de coletas
   - Executar scraping manualmente

### Dashboard Público

1. Acesse http://127.0.0.1:8000/dashboard/
2. Visualize os dados coletados através de:
   - Gráficos interativos
   - Tabelas ordenáveis
   - Filtros por data, fonte e palavra-chave
   - Visualizações detalhadas

### Executando Scraping Manualmente

Para executar o scraping manualmente:

```
python scripts\executar_scraping.py
```

Ou através do painel administrativo, clicando no botão "Executar Scraping".

## ⏱️ Configurando Agendamento Automático

Para configurar o agendamento automático de coletas usando o Task Scheduler do Windows:

1. Consulte o guia detalhado em `docs\configuracao_task_scheduler.md`
2. Ou execute o script de agendamento:
   ```
   executar_scraping.bat
   ```

## 📁 Estrutura de Diretórios

```
oraculo_dados/
│
├── administrativo/       # App de gestão do sistema
├── dashboard/           # App de visualização pública
├── scraper/             # App de coleta de dados
│   ├── management/      # Comandos personalizados
│   └── migrations/      # Migrações do banco de dados
│
├── oraculo_dados/       # Configurações do projeto
├── scripts/             # Scripts de utilidade
├── docs/                # Documentação
├── templates/           # Templates globais
├── static/              # Arquivos estáticos
│
├── db.sqlite3           # Banco de dados
├── manage.py            # Script de gerenciamento Django
├── requirements.txt     # Dependências do projeto
├── configurar_windows.bat  # Script de configuração para Windows
└── executar_scraping.bat   # Script para execução do scraping
```

## 🔍 Personalização

### Adicionando Novas Fontes

1. Acesse o painel administrativo
2. Vá para "Fontes" e clique em "Nova Fonte"
3. Preencha os campos:
   - Nome: Nome descritivo da fonte
   - URL: Endereço completo da página
   - Tipo: Selecione o tipo de fonte (notícia, blog, fórum, etc.)

### Configurando Palavras-chave

1. Acesse o painel administrativo
2. Vá para "Palavras-chave" e clique em "Nova Palavra-chave"
3. Preencha os campos:
   - String: Texto da palavra-chave
   - Categoria: Classificação da palavra-chave
   - Prioridade: Nível de importância

## 🛠️ Solução de Problemas

### Problemas com Selenium

Se encontrar problemas com o Selenium:

1. Verifique se o Chrome está instalado
2. Certifique-se de que o ChromeDriver está na versão compatível com seu Chrome
3. Ajuste as configurações em `scraper/scraper_utils.py` se necessário

### Erros de Banco de Dados

Se encontrar erros relacionados ao banco de dados:

1. Verifique se as migrações foram aplicadas:
   ```
   python manage.py migrate --check
   ```
2. Se necessário, recrie o banco de dados:
   ```
   del db.sqlite3
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Problemas de Agendamento

Se o agendamento automático não funcionar:

1. Verifique as permissões do Task Scheduler
2. Certifique-se de que os caminhos no script batch estão corretos
3. Teste a execução manual do script para identificar erros

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

Para suporte ou dúvidas, entre em contato através de:

- Email: suporte@oraculodedados.com
- GitHub: [github.com/oraculodedados](https://github.com/oraculodedados)

---