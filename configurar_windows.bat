@echo off
setlocal ENABLEEXTENSIONS
title Oráculo de Dados - Setup

REM ==========================================================
REM Script de Inicializacao do Projeto Oraculo de Dados
REM Compatível com Windows 11
REM ==========================================================

echo.
echo ============================================
echo   Iniciando configuracao do Oraculo de Dados
echo ============================================
echo.

REM Verificar se Python está disponível
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ e adicione ao PATH.
    goto :FIM
)

REM Verificar se pip está disponível
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] pip nao encontrado. Verifique sua instalacao do Python.
    goto :FIM
)

REM Criar ambiente virtual se nao existir
if not exist "venv\" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] ao criar o ambiente virtual.
        goto :FIM
    )
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call "venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] ao ativar ambiente virtual.
    goto :FIM
)

REM Instalar dependencias se existir o arquivo
if exist requirements.txt (
    echo Instalando dependencias do projeto...
    pip install --upgrade pip
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] ao instalar as dependencias.
        goto :FIM
    )
) else (
    echo [AVISO] Arquivo requirements.txt nao encontrado.
)

REM Verificar se Django está instalado
python -m django --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Django nao foi instalado corretamente.
    goto :FIM
)

REM Migrar banco de dados se nao existir
if not exist db.sqlite3 (
    echo Migrando banco de dados...
    python manage.py migrate
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] ao executar as migracoes.
        goto :FIM
    )

    echo Criando superusuario...
    echo (Voce sera solicitado a definir usuario e senha)
    python manage.py createsuperuser
)

echo.
echo ============================================
echo   Configuracao concluida com sucesso!
echo ============================================
echo.
echo COMANDOS DISPONIVEIS:
echo ---------------------
echo Iniciar servidor local:     python manage.py runserver
echo Executar scraping manual:  python scripts\executar_scraping.py
echo Agendamento automatico:    consulte docs\configuracao_task_scheduler.md
echo.
echo Ambiente virtual esta ativo. Para sair, digite: deactivate
echo.

goto :FIM

:FIM
echo.
echo Pressione qualquer tecla para finalizar...
pause >nul
endlocal
