import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scraper")

class ScraperBase:
    """Classe base para scrapers"""
    
    def __init__(self, url, palavras_chave=None, timeout=10):
        self.url = url
        self.palavras_chave = palavras_chave or []
        self.timeout = timeout
        self.conteudo = None
        self.soup = None
    
    def _contem_palavra_chave(self, texto):
        """Verifica se o texto contém alguma das palavras-chave"""
        if not self.palavras_chave:
            return True
        
        texto_lower = texto.lower()
        for palavra in self.palavras_chave:
            if palavra.lower() in texto_lower:
                return True
        return False
    
    def extrair_data(self, elemento):
        """Tenta extrair uma data de um elemento"""
        # Implementação básica, pode ser sobrescrita por subclasses
        return datetime.now()
    
    def processar_resultados(self, resultados):
        """Processa os resultados antes de retornar"""
        return [r for r in resultados if r.get('conteudo') and self._contem_palavra_chave(r.get('conteudo', ''))]


class ScraperHTTP(ScraperBase):
    """Scraper usando requests e BeautifulSoup"""
    
    def __init__(self, url, palavras_chave=None, timeout=10, headers=None):
        super().__init__(url, palavras_chave, timeout)
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def obter_pagina(self):
        """Obtém o conteúdo da página usando requests"""
        try:
            logger.info(f"Obtendo página: {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.conteudo = response.text
            self.soup = BeautifulSoup(self.conteudo, 'html.parser')
            return True
        except requests.RequestException as e:
            logger.error(f"Erro ao obter página {self.url}: {str(e)}")
            return False
    
    def extrair_conteudo(self, seletores):
        """Extrai conteúdo usando seletores CSS"""
        if not self.soup:
            if not self.obter_pagina():
                return []
        
        resultados = []
        
        for seletor in seletores:
            elementos = self.soup.select(seletor.get('container', 'body'))
            
            for elemento in elementos:
                try:
                    titulo_elem = elemento.select_one(seletor.get('titulo', ''))
                    titulo = titulo_elem.text.strip() if titulo_elem else "Sem título"
                    
                    link_elem = elemento.select_one(seletor.get('link', ''))
                    link = link_elem.get('href', '') if link_elem else ""
                    
                    # Normalizar URL relativa
                    if link and not (link.startswith('http://') or link.startswith('https://')):
                        if link.startswith('/'):
                            # URL relativa à raiz
                            from urllib.parse import urlparse
                            parsed_url = urlparse(self.url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            link = base_url + link
                        else:
                            # URL relativa ao caminho atual
                            link = self.url.rstrip('/') + '/' + link
                    
                    conteudo_elem = elemento.select_one(seletor.get('conteudo', ''))
                    conteudo = conteudo_elem.text.strip() if conteudo_elem else ""
                    
                    data_elem = elemento.select_one(seletor.get('data', ''))
                    data = self.extrair_data(data_elem) if data_elem else datetime.now()
                    
                    if titulo or conteudo:
                        resultados.append({
                            'titulo': titulo,
                            'link': link,
                            'conteudo': conteudo,
                            'data_publicacao': data
                        })
                except Exception as e:
                    logger.error(f"Erro ao extrair conteúdo: {str(e)}")
        
        return self.processar_resultados(resultados)


class ScraperSelenium(ScraperBase):
    """Scraper usando Selenium para sites dinâmicos"""
    
    def __init__(self, url, palavras_chave=None, timeout=10, espera_carregamento=5):
        super().__init__(url, palavras_chave, timeout)
        self.espera_carregamento = espera_carregamento
        self.driver = None
    
    def iniciar_driver(self):
        """Inicializa o driver do Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-infobars")
            
            # Configuração para Windows
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-features=NetworkService")
            
            # Configuração de User-Agent para Windows
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
            return True
        except Exception as e:
            logger.error(f"Erro ao inicializar driver Selenium: {str(e)}")
            return False
    
    def obter_pagina(self):
        """Obtém o conteúdo da página usando Selenium"""
        if not self.driver:
            if not self.iniciar_driver():
                return False
        
        try:
            logger.info(f"Obtendo página com Selenium: {self.url}")
            self.driver.get(self.url)
            
            # Espera para carregamento de conteúdo dinâmico
            time.sleep(self.espera_carregamento)
            
            self.conteudo = self.driver.page_source
            self.soup = BeautifulSoup(self.conteudo, 'html.parser')
            return True
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Erro ao obter página com Selenium {self.url}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado com Selenium: {str(e)}")
            return False
    
    def extrair_conteudo(self, seletores):
        """Extrai conteúdo usando seletores CSS via Selenium"""
        if not self.soup:
            if not self.obter_pagina():
                return []
        
        resultados = []
        
        for seletor in seletores:
            try:
                # Esperar pelo contêiner principal
                container_selector = seletor.get('container', 'body')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
                )
                
                # Obter elementos do contêiner
                elementos = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                
                for elemento in elementos:
                    try:
                        titulo = ""
                        if seletor.get('titulo'):
                            titulo_elems = elemento.find_elements(By.CSS_SELECTOR, seletor.get('titulo'))
                            if titulo_elems:
                                titulo = titulo_elems[0].text.strip()
                        
                        link = ""
                        if seletor.get('link'):
                            link_elems = elemento.find_elements(By.CSS_SELECTOR, seletor.get('link'))
                            if link_elems:
                                link = link_elems[0].get_attribute('href') or ""
                        
                        conteudo = ""
                        if seletor.get('conteudo'):
                            conteudo_elems = elemento.find_elements(By.CSS_SELECTOR, seletor.get('conteudo'))
                            if conteudo_elems:
                                conteudo = conteudo_elems[0].text.strip()
                        
                        data = datetime.now()
                        if seletor.get('data'):
                            data_elems = elemento.find_elements(By.CSS_SELECTOR, seletor.get('data'))
                            if data_elems:
                                data = self.extrair_data(data_elems[0])
                        
                        if titulo or conteudo:
                            resultados.append({
                                'titulo': titulo,
                                'link': link,
                                'conteudo': conteudo,
                                'data_publicacao': data
                            })
                    except Exception as e:
                        logger.error(f"Erro ao extrair elemento: {str(e)}")
            except Exception as e:
                logger.error(f"Erro ao processar seletor: {str(e)}")
        
        return self.processar_resultados(resultados)
    
    def fechar(self):
        """Fecha o driver do Selenium"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")


class ScraperFactory:
    """Fábrica para criar scrapers apropriados"""
    
    @staticmethod
    def criar_scraper(url, config):
        """Cria um scraper baseado na configuração"""
        tipo_scraper = config.get('tipo', 'http')
        palavras_chave = config.get('palavras_chave', [])
        timeout = config.get('timeout', 10)
        
        if tipo_scraper == 'selenium':
            espera = config.get('espera_carregamento', 5)
            return ScraperSelenium(url, palavras_chave, timeout, espera)
        else:
            headers = config.get('headers', None)
            return ScraperHTTP(url, palavras_chave, timeout, headers)
