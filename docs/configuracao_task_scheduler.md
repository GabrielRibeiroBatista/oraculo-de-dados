# Guia de Configuração do Task Scheduler do Windows para o Oráculo de Dados

Este documento explica como configurar o agendamento automático de scraping usando o Task Scheduler do Windows.

## Pré-requisitos

- Windows 10 ou Windows 11
- Python 3.10 ou superior instalado
- Projeto Oráculo de Dados configurado

## Passos para Configuração

### 1. Preparar o Script de Execução

O projeto já inclui dois arquivos para execução do scraping:

- `executar_scraping.bat` - Script batch para execução via linha de comando
- `scripts/executar_scraping.py` - Script Python que pode ser chamado diretamente

### 2. Abrir o Task Scheduler do Windows

1. Pressione `Win + R` para abrir a caixa de diálogo Executar
2. Digite `taskschd.msc` e pressione Enter
3. O Task Scheduler será aberto

### 3. Criar uma Nova Tarefa

1. No painel direito, clique em "Criar Tarefa Básica..."
2. Dê um nome à tarefa, por exemplo: "Oráculo de Dados - Scraping Automático"
3. Adicione uma descrição (opcional): "Executa o scraping automático do Oráculo de Dados"
4. Clique em "Avançar"

### 4. Configurar o Gatilho (Trigger)

1. Selecione a frequência desejada (Diariamente, Semanalmente, etc.)
2. Configure os detalhes do agendamento:
   - Para execução diária: defina o horário (ex: 08:00)
   - Para execução semanal: selecione os dias da semana
   - Para execução mais frequente: escolha "Diariamente" e depois edite a tarefa para configurar intervalos menores
3. Clique em "Avançar"

### 5. Configurar a Ação

1. Selecione "Iniciar um programa"
2. Clique em "Avançar"
3. Em "Programa/script", clique em "Procurar" e selecione o arquivo `executar_scraping.bat` no diretório do projeto
4. Em "Iniciar em", digite o caminho completo para o diretório do projeto (ex: `C:\Projetos\oraculo_dados`)
5. Clique em "Avançar"

### 6. Finalizar a Configuração

1. Revise as configurações
2. Marque a opção "Abrir o diálogo de propriedades desta tarefa quando eu clicar em Concluir"
3. Clique em "Concluir"

### 7. Configurações Adicionais

Na janela de propriedades que se abre:

1. Na aba "Geral", marque:
   - "Executar com privilégios mais altos"
   - "Executar independentemente do usuário estar conectado ou não"
2. Na aba "Condições", desmarque:
   - "Iniciar a tarefa somente se o computador estiver ocioso por"
   - "Parar se o computador começar a funcionar com bateria"
3. Na aba "Configurações", marque:
   - "Executar tarefa o mais rápido possível após um início agendado ser perdido"
4. Clique em "OK" para salvar as configurações

## Configuração Alternativa (Mais Avançada)

Para maior controle, você pode configurar o Task Scheduler para executar o script Python diretamente:

1. Em "Programa/script", digite o caminho completo para o executável Python (ex: `C:\Python310\python.exe`)
2. Em "Adicionar argumentos", digite o caminho para o script Python (ex: `scripts\executar_scraping.py`)
3. Em "Iniciar em", digite o caminho completo para o diretório do projeto

## Verificação

Para verificar se a tarefa está funcionando corretamente:

1. Clique com o botão direito na tarefa e selecione "Executar"
2. Verifique o status de execução
3. Verifique os logs do sistema para confirmar que o scraping foi executado com sucesso

## Solução de Problemas

Se a tarefa não for executada conforme esperado:

1. Verifique se os caminhos estão corretos
2. Certifique-se de que o ambiente virtual está configurado corretamente no script batch
3. Verifique os logs de erro no Task Scheduler
4. Teste a execução manual do script batch para confirmar que funciona corretamente
