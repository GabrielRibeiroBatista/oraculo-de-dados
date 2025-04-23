from django.core.management.base import BaseCommand
from scraper.models import Fonte, PalavraChave, EntradaColetada
from scraper.scraper_utils import ScraperFactory
import logging
import traceback
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_command.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scraper_command")

class Command(BaseCommand):
    help = 'Executa o scraping de fontes cadastradas no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fonte-id',
            type=int,
            help='ID da fonte específica para fazer scraping (opcional)',
        )
        parser.add_argument(
            '--palavra-chave-id',
            type=int,
            help='ID da palavra-chave específica para filtrar (opcional)',
        )
        parser.add_argument(
            '--todas',
            action='store_true',
            help='Executa scraping em todas as fontes ativas',
        )

    def handle(self, *args, **options):
        fonte_id = options.get('fonte_id')
        palavra_chave_id = options.get('palavra_chave_id')
        todas = options.get('todas')

        # Definir quais fontes serão processadas
        if fonte_id:
            fontes = Fonte.objects.filter(id=fonte_id, ativo=True)
            if not fontes.exists():
                self.stdout.write(self.style.ERROR(f'Fonte com ID {fonte_id} não encontrada ou inativa'))
                return
        elif todas:
            fontes = Fonte.objects.filter(ativo=True)
        else:
            self.stdout.write(self.style.ERROR('Especifique --fonte-id=ID ou --todas para executar o scraping'))
            return

        # Definir quais palavras-chave serão usadas
        if palavra_chave_id:
            palavras_chave = PalavraChave.objects.filter(id=palavra_chave_id, ativo=True)
            if not palavras_chave.exists():
                self.stdout.write(self.style.ERROR(f'Palavra-chave com ID {palavra_chave_id} não encontrada ou inativa'))
                return
        else:
            palavras_chave = PalavraChave.objects.filter(ativo=True)

        # Lista de strings de palavras-chave
        palavras_chave_strings = [p.string for p in palavras_chave]

        # Processar cada fonte
        total_entradas = 0
        for fonte in fontes:
            try:
                self.stdout.write(self.style.NOTICE(f'Processando fonte: {fonte.nome} ({fonte.url})'))
                
                # Configuração do scraper baseada no tipo da fonte
                config = {
                    'tipo': 'selenium' if fonte.tipo in ['rede_social', 'forum'] else 'http',
                    'palavras_chave': palavras_chave_strings,
                    'timeout': 15,
                    'espera_carregamento': 5
                }
                
                # Seletores CSS para diferentes tipos de fonte
                seletores = self._obter_seletores_por_tipo(fonte.tipo)
                
                # Criar e executar o scraper
                scraper = ScraperFactory.criar_scraper(fonte.url, config)
                resultados = scraper.extrair_conteudo(seletores)
                
                # Fechar o driver do Selenium se aplicável
                if hasattr(scraper, 'fechar'):
                    scraper.fechar()
                
                # Salvar resultados no banco de dados
                entradas_salvas = self._salvar_resultados(fonte, resultados, palavras_chave)
                total_entradas += entradas_salvas
                
                self.stdout.write(self.style.SUCCESS(f'Fonte {fonte.nome}: {entradas_salvas} entradas coletadas'))
                
            except Exception as e:
                logger.error(f"Erro ao processar fonte {fonte.nome}: {str(e)}")
                logger.error(traceback.format_exc())
                self.stdout.write(self.style.ERROR(f'Erro ao processar fonte {fonte.nome}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Scraping concluído. Total de {total_entradas} entradas coletadas.'))

    def _obter_seletores_por_tipo(self, tipo_fonte):
        """Retorna seletores CSS apropriados para o tipo de fonte"""
        seletores_padrao = [{
            'container': 'article, .post, .entry, .item, .card',
            'titulo': 'h1, h2, h3, .title, .headline',
            'link': 'a, .link',
            'conteudo': 'p, .content, .text, .description',
            'data': '.date, .time, time, .published'
        }]
        
        # Seletores específicos por tipo de fonte
        seletores_por_tipo = {
            'noticia': [{
                'container': 'article, .news-item, .article-item',
                'titulo': 'h1, h2, h3, .article-title, .headline',
                'link': 'a, .article-link',
                'conteudo': 'p, .article-content, .summary, .description',
                'data': '.date, time, .published-date'
            }],
            'blog': [{
                'container': '.post, .blog-entry, .blog-post',
                'titulo': 'h1, h2, .post-title, .entry-title',
                'link': 'a, .post-link, .permalink',
                'conteudo': 'p, .post-content, .entry-content, .summary',
                'data': '.date, .post-date, time, .published'
            }],
            'forum': [{
                'container': '.thread, .topic, .discussion, .forum-post',
                'titulo': 'h1, h2, .thread-title, .topic-title',
                'link': 'a, .thread-link',
                'conteudo': 'p, .post-content, .message, .post-message',
                'data': '.date, .post-date, time, .timestamp'
            }],
            'rede_social': [{
                'container': '.post, .tweet, .status, .feed-item',
                'titulo': 'h1, h2, .post-title, .user-name',
                'link': 'a, .post-link, .permalink',
                'conteudo': 'p, .post-content, .tweet-text, .status-content',
                'data': '.date, .post-date, time, .timestamp'
            }]
        }
        
        return seletores_por_tipo.get(tipo_fonte, seletores_padrao)

    def _salvar_resultados(self, fonte, resultados, palavras_chave_queryset):
        """Salva os resultados do scraping no banco de dados"""
        contador = 0
        
        for resultado in resultados:
            # Verificar se a entrada já existe pelo link
            if EntradaColetada.objects.filter(link_relacionado=resultado['link']).exists():
                continue
            
            # Criar nova entrada
            try:
                entrada = EntradaColetada(
                    fonte=fonte,
                    titulo=resultado['titulo'][:255],  # Limitar ao tamanho do campo
                    conteudo=resultado['conteudo'],
                    data_publicacao=resultado.get('data_publicacao'),
                    link_relacionado=resultado['link']
                )
                entrada.save()
                
                # Associar palavras-chave encontradas no conteúdo
                conteudo_lower = resultado['conteudo'].lower()
                for palavra_chave in palavras_chave_queryset:
                    if palavra_chave.string.lower() in conteudo_lower:
                        entrada.palavras_chave.add(palavra_chave)
                
                contador += 1
            except Exception as e:
                logger.error(f"Erro ao salvar entrada: {str(e)}")
        
        return contador
