import os
import sys
import django

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oraculo_dados.settings')
django.setup()

# Importar após configuração do Django
from django.core.management import call_command

def main():
    """
    Script Python para executar o scraping do Oráculo de Dados
    Para uso com o Task Scheduler do Windows ou execução manual
    """
    print(f"Iniciando scraping do Oráculo de Dados...")
    
    try:
        # Executar o comando de scraping com todas as fontes ativas
        call_command('executar_scraping', todas=True)
        print(f"Scraping concluído com sucesso!")
    except Exception as e:
        print(f"Erro durante execução do scraping: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
