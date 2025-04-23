import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management import call_command
from django.db import connection
import sys
import os
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduler")

def executar_scraping_agendado():
    """Função que será executada pelo agendador"""
    try:
        logger.info(f"Iniciando scraping agendado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fechar conexões antigas com o banco de dados
        connection.close()
        
        # Executar o comando de scraping
        call_command('executar_scraping', todas=True)
        
        logger.info(f"Scraping agendado concluído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Erro durante execução do scraping agendado: {str(e)}")

def iniciar_agendador():
    """Inicia o agendador de tarefas"""
    try:
        # Verificar se estamos em ambiente de desenvolvimento
        if settings.DEBUG:
            logger.info("Iniciando agendador de tarefas em modo de desenvolvimento")
            
            # Criar o agendador
            scheduler = BackgroundScheduler()
            
            # Adicionar tarefa para executar a cada hora
            # Usando CronTrigger para maior flexibilidade
            scheduler.add_job(
                executar_scraping_agendado,
                trigger=CronTrigger(hour='*/1'),  # A cada hora
                id='scraping_agendado',
                max_instances=1,
                replace_existing=True,
            )
            
            # Iniciar o agendador
            scheduler.start()
            logger.info("Agendador de tarefas iniciado com sucesso")
            
            return scheduler
        else:
            logger.info("Ambiente de produção detectado, agendador não iniciado automaticamente")
            return None
    except Exception as e:
        logger.error(f"Erro ao iniciar agendador: {str(e)}")
        return None

# Variável para armazenar a instância do agendador
scheduler = None

# Iniciar o agendador apenas se não estivermos executando comandos de gerenciamento
# Isso evita que o agendador seja iniciado durante migrações ou outros comandos
if 'runserver' in sys.argv or 'manage.py' not in sys.argv:
    scheduler = iniciar_agendador()

# Função para uso em scripts externos (como Task Scheduler do Windows)
def executar_scraping_externo():
    """
    Função para ser chamada por agendadores externos como o Task Scheduler do Windows
    
    Exemplo de uso com Task Scheduler:
    - Programa/script: python
    - Argumentos: C:\caminho\para\projeto\scripts\executar_scraping.py
    - Iniciar em: C:\caminho\para\projeto\
    """
    # Configurar ambiente Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oraculo_dados.settings')
    import django
    django.setup()
    
    # Executar scraping
    from django.core.management import call_command
    call_command('executar_scraping', todas=True)

# Se este arquivo for executado diretamente, executar o scraping
if __name__ == "__main__":
    executar_scraping_externo()
