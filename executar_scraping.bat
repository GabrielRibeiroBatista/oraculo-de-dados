@echo off
REM Script para executar o scraping do Oráculo de Dados
REM Para uso com o Task Scheduler do Windows

REM Definir o diretório do projeto
set PROJETO_DIR=%~dp0
cd %PROJETO_DIR%

REM Ativar o ambiente virtual
call venv\Scripts\activate.bat

REM Executar o script de scraping
python scraper\scheduler.py

REM Desativar o ambiente virtual
call venv\Scripts\deactivate.bat

echo Scraping concluído em %date% %time%
